// POST /api/sell-upload — admin uploads a product file to R2
function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const formData = await request.formData();
        const password = formData.get('password');
        const file = formData.get('file');
        const title = (formData.get('title') || '').trim();
        const description = (formData.get('description') || '').trim();
        const priceInput = formData.get('price');
        const currency = (formData.get('currency') || 'usdc').toLowerCase();

        // Auth
        if (password !== env.ADMIN_PASSWORD) {
            return json({ error: 'Invalid password' }, 401);
        }

        // Validate
        if (!file) return json({ error: 'No file provided' }, 400);
        if (!title) return json({ error: 'Title is required' }, 400);

        const priceFloat = parseFloat(priceInput);
        if (!priceFloat || priceFloat <= 0) {
            return json({ error: 'Price must be greater than 0' }, 400);
        }

        if (currency !== 'usdc' && currency !== 'eth') {
            return json({ error: 'Currency must be usdc or eth' }, 400);
        }

        // Convert to atomic units
        let price, priceDisplay;
        if (currency === 'usdc') {
            price = Math.round(priceFloat * 1e6); // 6 decimals
            priceDisplay = `${priceFloat} USDC`;
        } else {
            price = BigInt(Math.round(priceFloat * 1e18)).toString(); // wei as string
            priceDisplay = `${priceFloat} ETH`;
        }

        // Generate product ID
        const productId = crypto.randomUUID().split('-')[0];

        // Upload to R2
        const r2Key = `products/${productId}/${file.name}`;
        await env.FILES.put(r2Key, file.stream(), {
            httpMetadata: { contentType: file.type || 'application/octet-stream' }
        });

        // Store metadata in KV
        const product = {
            id: productId,
            title,
            description,
            price,
            currency,
            priceDisplay,
            r2Key,
            filename: file.name,
            contentType: file.type || 'application/octet-stream',
            fileSize: file.size,
            createdAt: Date.now(),
            active: true
        };

        await env.COMMENTS.put(`product:${productId}`, JSON.stringify(product));

        // Update index
        const index = await env.COMMENTS.get('products:index', 'json') || [];
        index.push(productId);
        await env.COMMENTS.put('products:index', JSON.stringify(index));

        return json({ success: true, productId, priceDisplay });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
