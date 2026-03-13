// GET /api/download?token=xxx&file=0 — validate token and stream file from R2
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
    }
    if (!p.files) p.files = [];
    return p;
}

export async function onRequestGet(context) {
    const { request, env } = context;
    const url = new URL(request.url);
    const token = url.searchParams.get('token');
    const fileIndex = parseInt(url.searchParams.get('file') || '0', 10);

    if (!token) return json({ error: 'Missing token' }, 400);

    try {
        const tokenKey = `dltoken:${token}`;
        const tokenData = await env.COMMENTS.get(tokenKey, 'json');

        if (!tokenData) {
            return json({ error: 'Invalid or expired download token' }, 403);
        }

        if (Date.now() > tokenData.expiresAt) {
            await env.COMMENTS.delete(tokenKey);
            return json({ error: 'Download token has expired' }, 403);
        }

        if (tokenData.downloadsRemaining <= 0) {
            await env.COMMENTS.delete(tokenKey);
            return json({ error: 'Download limit reached' }, 403);
        }

        // Look up product
        const product = normalize(await env.COMMENTS.get(`product:${tokenData.productId}`, 'json'));
        if (!product) {
            return json({ error: 'Product not found' }, 404);
        }

        if (fileIndex < 0 || fileIndex >= product.files.length) {
            return json({ error: 'File index out of range' }, 400);
        }

        const file = product.files[fileIndex];

        // Fetch from R2
        const object = await env.FILES.get(file.r2Key);
        if (!object) {
            return json({ error: 'File not found' }, 404);
        }

        // Decrement downloads remaining
        tokenData.downloadsRemaining--;
        await env.COMMENTS.put(tokenKey, JSON.stringify(tokenData), {
            expirationTtl: Math.max(1, Math.floor((tokenData.expiresAt - Date.now()) / 1000))
        });

        // Stream file
        return new Response(object.body, {
            headers: {
                'Content-Type': file.contentType || 'application/octet-stream',
                'Content-Disposition': `attachment; filename="${file.filename}"`,
                'Cache-Control': 'no-store',
                'Content-Length': file.fileSize
            }
        });

    } catch (error) {
        return json({ error: error.message }, 500);
    }
}
