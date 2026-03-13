// GET /api/product-image?id=xxx — serve product display image from R2
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

    if (!id) return json({ error: 'Missing product id' }, 400);

    try {
        const product = await env.COMMENTS.get(`product:${id}`, 'json');
        if (!product || !product.imageKey) {
            return new Response(null, { status: 404 });
        }

        const object = await env.FILES.get(product.imageKey);
        if (!object) {
            return new Response(null, { status: 404 });
        }

        return new Response(object.body, {
            headers: {
                'Content-Type': object.httpMetadata?.contentType || 'image/jpeg',
                'Cache-Control': 'public, max-age=86400'
            }
        });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
