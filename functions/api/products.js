// GET /api/products — list all products or single product by id
function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

export async function onRequestGet(context) {
    const { request, env } = context;
    const url = new URL(request.url);
    const id = url.searchParams.get('id');

    try {
        if (id) {
            // Single product mode (for embeds)
            const product = await env.COMMENTS.get(`product:${id}`, 'json');
            if (!product || !product.active) {
                return json({ error: 'Product not found' }, 404);
            }
            const { r2Key, ...publicProduct } = product;
            return json({ product: publicProduct });
        }

        // List mode
        const index = await env.COMMENTS.get('products:index', 'json') || [];
        const products = [];

        for (const productId of index) {
            const product = await env.COMMENTS.get(`product:${productId}`, 'json');
            if (product && product.active) {
                const { r2Key, ...publicProduct } = product;
                products.push(publicProduct);
            }
        }

        return json({ products });
    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
