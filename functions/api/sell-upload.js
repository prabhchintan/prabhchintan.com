// POST /api/sell-upload — admin uploads a product with multiple files + optional image to R2
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
        const title = (formData.get('title') || '').trim();
        const description = (formData.get('description') || '').trim();
        const priceInput = formData.get('price');
        const currency = (formData.get('currency') || 'usdc').toLowerCase();
        const files = formData.getAll('file');
        const image = formData.get('image');

        // Auth
        if (password !== env.ADMIN_PASSWORD) {
            return json({ error: 'Invalid password' }, 401);
        }

        // Validate
        if (!files.length || !files[0]?.name) return json({ error: 'No files provided' }, 400);
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
            price = Math.round(priceFloat * 1e6);
            priceDisplay = `${priceFloat} USDC`;
        } else {
            price = BigInt(Math.round(priceFloat * 1e18)).toString();
            priceDisplay = `${priceFloat} ETH`;
        }

        const productId = crypto.randomUUID().split('-')[0];

        // Upload files to R2
        const productFiles = [];
        for (const file of files) {
            if (!file?.name) continue;
            const r2Key = `products/${productId}/${file.name}`;
            await env.FILES.put(r2Key, file.stream(), {
                httpMetadata: { contentType: file.type || 'application/octet-stream' }
            });
            productFiles.push({
                r2Key,
                filename: file.name,
                contentType: file.type || 'application/octet-stream',
                fileSize: file.size
            });
        }

        // Upload image to R2 if provided
        let imageKey = null;
        if (image && image.name) {
            const ext = image.name.split('.').pop().toLowerCase();
            imageKey = `products/${productId}/image.${ext}`;
            await env.FILES.put(imageKey, image.stream(), {
                httpMetadata: { contentType: image.type || 'image/jpeg' }
            });
        }

        // Store metadata in KV
        const product = {
            id: productId,
            title,
            description,
            price,
            currency,
            priceDisplay,
            files: productFiles,
            createdAt: Date.now(),
            active: true
        };
        if (imageKey) product.imageKey = imageKey;

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
