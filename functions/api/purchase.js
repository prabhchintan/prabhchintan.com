// POST /api/purchase — verify payment and issue download token
const RECIPIENT = '0x3570958b8dcbc4f663f508efcedb454ee9af9516';
const TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';

const CHAINS = {
    1:     { rpc: 'https://eth.llamarpc.com',    usdc: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' },
    8453:  { rpc: 'https://mainnet.base.org',     usdc: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913' },
    42161: { rpc: 'https://arb1.arbitrum.io/rpc', usdc: '0xaf88d065e77c8cc2239327c5edb3a432268e5831' },
    10:    { rpc: 'https://mainnet.optimism.io',  usdc: '0x0b2c639c533813f4aa9d7837caf62653d097ff85' },
    137:   { rpc: 'https://polygon-rpc.com',      usdc: '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359' }
};

function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

async function rpcCall(rpc, method, params) {
    const resp = await fetch(rpc, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 })
    });
    const { result } = await resp.json();
    return result;
}

async function verifyUsdcPayment(txHash, address, chain, requiredAmount) {
    const receipt = await rpcCall(chain.rpc, 'eth_getTransactionReceipt', [txHash]);

    if (!receipt) return { valid: false, reason: 'Transaction not found' };
    if (receipt.status !== '0x1') return { valid: false, reason: 'Transaction failed on chain' };

    const senderPadded = '0x' + address.slice(2).toLowerCase().padStart(64, '0');
    const recipientPadded = '0x' + RECIPIENT.slice(2).padStart(64, '0');

    for (const log of (receipt.logs || [])) {
        if (log.address.toLowerCase() !== chain.usdc) continue;
        if (!log.topics || log.topics[0] !== TRANSFER_TOPIC) continue;
        if (log.topics[1]?.toLowerCase() !== senderPadded) continue;
        if (log.topics[2]?.toLowerCase() !== recipientPadded) continue;

        const amount = parseInt(log.data, 16);
        if (amount >= requiredAmount) {
            return { valid: true };
        }
    }

    return { valid: false, reason: 'No valid USDC transfer to recipient found' };
}

async function verifyEthPayment(txHash, address, chain, requiredAmount) {
    const tx = await rpcCall(chain.rpc, 'eth_getTransaction', [txHash]);

    if (!tx) return { valid: false, reason: 'Transaction not found' };

    if (tx.to?.toLowerCase() !== RECIPIENT) {
        return { valid: false, reason: 'Transaction recipient mismatch' };
    }

    const valueSent = BigInt(tx.value);
    const required = BigInt(requiredAmount);
    if (valueSent < required) {
        return { valid: false, reason: 'Insufficient ETH amount' };
    }

    // Verify tx succeeded
    const receipt = await rpcCall(chain.rpc, 'eth_getTransactionReceipt', [txHash]);
    if (!receipt || receipt.status !== '0x1') {
        return { valid: false, reason: 'Transaction failed on chain' };
    }

    return { valid: true };
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { productId, txHash, address, chainId } = await request.json();

        if (!productId || !txHash || !address || !chainId) {
            return json({ error: 'Missing required fields' }, 400);
        }

        if (!/^0x[a-f0-9]{64}$/i.test(txHash)) {
            return json({ error: 'Invalid transaction hash' }, 400);
        }

        if (!/^0x[a-f0-9]{40}$/i.test(address)) {
            return json({ error: 'Invalid address' }, 400);
        }

        const chain = CHAINS[chainId];
        if (!chain) return json({ error: 'Unsupported chain' }, 400);

        // Look up product
        const product = await env.COMMENTS.get(`product:${productId}`, 'json');
        if (!product || !product.active) {
            return json({ error: 'Product not found' }, 404);
        }

        // Check tx not already used
        const txKey = `tx:${txHash.toLowerCase()}`;
        const txUsed = await env.COMMENTS.get(txKey);
        if (txUsed) {
            return json({ error: 'Transaction already used' }, 400);
        }

        // Verify payment based on currency
        let verification;
        if (product.currency === 'usdc') {
            verification = await verifyUsdcPayment(txHash, address, chain, product.price);
        } else {
            verification = await verifyEthPayment(txHash, address, chain, product.price);
        }

        if (!verification.valid) {
            return json({ error: verification.reason }, 400);
        }

        // Mark tx as used
        await env.COMMENTS.put(txKey, `purchase:${productId}`);

        // Issue download token
        const downloadToken = crypto.randomUUID();
        const now = Date.now();
        const tokenData = {
            productId,
            address: address.toLowerCase(),
            txHash: txHash.toLowerCase(),
            chainId,
            createdAt: now,
            expiresAt: now + 24 * 60 * 60 * 1000, // 24h
            downloadsRemaining: 3
        };

        await env.COMMENTS.put(`dltoken:${downloadToken}`, JSON.stringify(tokenData), {
            expirationTtl: 86400 // 24h in seconds
        });

        return json({ success: true, downloadToken });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
