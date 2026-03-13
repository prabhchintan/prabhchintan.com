// GET /api/products — list all products or single product by id
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

function toPublic(p) {
    p = normalize(p);
    const result = {
        id: p.id,
        title: p.title,
        description: p.description,
        price: p.price,
        currency: p.currency,
        priceDisplay: p.priceDisplay,
        files: p.files.map(f => ({ filename: f.filename, fileSize: f.fileSize })),
        totalFileSize: p.files.reduce((sum, f) => sum + (f.fileSize || 0), 0),
        createdAt: p.createdAt
    };
    if (p.imageKey) result.imageUrl = `/api/product-image?id=${p.id}`;
    return result;
}

export async function onRequestGet(context) {
    const { request, env } = context;
    const url = new URL(request.url);
    const id = url.searchParams.get('id');

    try {
        if (id) {
            const product = await env.COMMENTS.get(`product:${id}`, 'json');
            if (!product || !product.active) {
                return json({ error: 'Product not found' }, 404);
            }
            return json({ product: toPublic(product) });
        }

        const index = await env.COMMENTS.get('products:index', 'json') || [];
        const products = [];

        for (const productId of index) {
            const product = await env.COMMENTS.get(`product:${productId}`, 'json');
            if (product && product.active) {
                products.push(toPublic(product));
            }
        }

        return json({ products });
    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
