const RECIPIENT = '0xbc82b52fd791757de5002bcfaa5738776f63c440';
const USDC_BASE = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913';
const TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BASE_RPC = 'https://mainnet.base.org';
const MIN_AMOUNT = 1000000; // 1 USDC (6 decimals)

function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

// GET /api/comments?slug=xxx
export async function onRequestGet(context) {
    const { request, env } = context;
    const url = new URL(request.url);
    const slug = url.searchParams.get('slug');

    if (!slug || !/^[a-z0-9-]+$/i.test(slug)) {
        return json({ error: 'Invalid slug' }, 400);
    }

    const data = await env.COMMENTS.get(`slug:${slug}`, 'json');
    return json({ comments: data?.comments || [] });
}

// POST /api/comments
export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { slug, name, text, txHash, address } = await request.json();

        // Validate required fields
        if (!slug || !text || !txHash || !address) {
            return json({ error: 'Missing required fields' }, 400);
        }

        if (!/^[a-z0-9-]+$/i.test(slug)) {
            return json({ error: 'Invalid slug' }, 400);
        }

        if (!/^0x[a-f0-9]{64}$/i.test(txHash)) {
            return json({ error: 'Invalid transaction hash' }, 400);
        }

        if (!/^0x[a-f0-9]{40}$/i.test(address)) {
            return json({ error: 'Invalid address' }, 400);
        }

        // Check tx not already used
        const txKey = `tx:${txHash.toLowerCase()}`;
        const txUsed = await env.COMMENTS.get(txKey);
        if (txUsed) {
            return json({ error: 'Transaction already used for a comment' }, 400);
        }

        // Verify tx on-chain (also checks sender matches)
        const verification = await verifyTransaction(txHash, address);
        if (!verification.valid) {
            return json({ error: verification.reason }, 400);
        }

        // Sanitize inputs
        const sanitizedName = (name || '').trim().slice(0, 50).replace(/<[^>]*>/g, '');
        const sanitizedText = text.trim().slice(0, 2000).replace(/<[^>]*>/g, '');

        if (!sanitizedText) {
            return json({ error: 'Comment text is empty' }, 400);
        }

        // Store comment
        const data = await env.COMMENTS.get(`slug:${slug}`, 'json') || { comments: [] };
        const comment = {
            id: crypto.randomUUID(),
            name: sanitizedName,
            text: sanitizedText,
            address: address.toLowerCase(),
            txHash: txHash.toLowerCase(),
            timestamp: Date.now()
        };
        data.comments.push(comment);

        await env.COMMENTS.put(`slug:${slug}`, JSON.stringify(data));
        await env.COMMENTS.put(txKey, slug);

        return json({ success: true, comment });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}

async function verifyTransaction(txHash, senderAddress) {
    const resp = await fetch(BASE_RPC, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'eth_getTransactionReceipt',
            params: [txHash],
            id: 1
        })
    });

    const { result } = await resp.json();

    if (!result) {
        return { valid: false, reason: 'Transaction not found on Base' };
    }

    if (result.status !== '0x1') {
        return { valid: false, reason: 'Transaction failed on chain' };
    }

    // Look for USDC Transfer event from sender to recipient
    const senderPadded = '0x' + senderAddress.slice(2).toLowerCase().padStart(64, '0');
    const recipientPadded = '0x' + RECIPIENT.slice(2).padStart(64, '0');

    for (const log of (result.logs || [])) {
        if (log.address.toLowerCase() !== USDC_BASE) continue;
        if (!log.topics || log.topics[0] !== TRANSFER_TOPIC) continue;
        if (log.topics[1]?.toLowerCase() !== senderPadded) continue;
        if (log.topics[2]?.toLowerCase() !== recipientPadded) continue;

        const amount = parseInt(log.data, 16);
        if (amount >= MIN_AMOUNT) {
            return { valid: true };
        }
    }

    return { valid: false, reason: 'No valid USDC transfer to recipient found' };
}
