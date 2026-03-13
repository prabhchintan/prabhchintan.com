// POST /api/edit-product — admin edits an existing product
function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

// Normalize old single-file format to files array
function normalize(p) {
    if (!p.files && p.r2Key) {
        p.files = [{ r2Key: p.r2Key, filename: p.filename, contentType: p.contentType, fileSize: p.fileSize }];
        delete p.r2Key; delete p.filename; delete p.contentType; delete p.fileSize;
    }
    if (!p.files) p.files = [];
    return p;
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const formData = await request.formData();
        const password = formData.get('password');
        const productId = formData.get('productId');

        if (password !== env.ADMIN_PASSWORD) {
            return json({ error: 'Invalid password' }, 401);
        }

        if (!productId) return json({ error: 'Product ID is required' }, 400);

        const product = await env.COMMENTS.get(`product:${productId}`, 'json');
        if (!product) return json({ error: 'Product not found' }, 404);

        normalize(product);

        // Update metadata fields
        const title = formData.get('title');
        const description = formData.get('description');
        const priceInput = formData.get('price');
        const currency = formData.get('currency');

        if (title !== null) product.title = title.trim();
        if (description !== null) product.description = description.trim();

        if (priceInput !== null && currency !== null) {
            const priceFloat = parseFloat(priceInput);
            const curr = currency.toLowerCase();
            if (priceFloat > 0 && (curr === 'usdc' || curr === 'eth')) {
                product.currency = curr;
                if (curr === 'usdc') {
                    product.price = Math.round(priceFloat * 1e6);
                    product.priceDisplay = `${priceFloat} USDC`;
                } else {
                    product.price = BigInt(Math.round(priceFloat * 1e18)).toString();
                    product.priceDisplay = `${priceFloat} ETH`;
                }
            }
        }

        // Remove files by filename
        const removeFiles = formData.getAll('removeFile');
        for (const filename of removeFiles) {
            const idx = product.files.findIndex(f => f.filename === filename);
            if (idx >= 0) {
                await env.FILES.delete(product.files[idx].r2Key);
                product.files.splice(idx, 1);
            }
        }

        // Add new files
        const newFiles = formData.getAll('file');
        for (const file of newFiles) {
            if (!file?.name) continue;
            const r2Key = `products/${productId}/${file.name}`;
            await env.FILES.put(r2Key, file.stream(), {
                httpMetadata: { contentType: file.type || 'application/octet-stream' }
            });
            product.files.push({
                r2Key,
                filename: file.name,
                contentType: file.type || 'application/octet-stream',
                fileSize: file.size
            });
        }

        // Handle image
        if (formData.get('removeImage') === '1' && product.imageKey) {
            await env.FILES.delete(product.imageKey);
            delete product.imageKey;
        }

        const image = formData.get('image');
        if (image && image.name) {
            // Remove old image first
            if (product.imageKey) {
                await env.FILES.delete(product.imageKey);
            }
            const ext = image.name.split('.').pop().toLowerCase();
            product.imageKey = `products/${productId}/image.${ext}`;
            await env.FILES.put(product.imageKey, image.stream(), {
                httpMetadata: { contentType: image.type || 'image/jpeg' }
            });
        }

        await env.COMMENTS.put(`product:${productId}`, JSON.stringify(product));

        return json({ success: true, productId });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
