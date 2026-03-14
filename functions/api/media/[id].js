// GET /api/media/:id — serve media from R2 with Range support and caching

export async function onRequestGet(context) {
    const { params, env, request } = context;
    const id = params.id;

    if (!id) {
        return new Response('Not found', { status: 404 });
    }

    try {
        // Look up metadata in KV
        const meta = await env.COMMENTS.get(`media:${id}`, 'json');
        if (!meta) {
            return new Response('Not found', { status: 404 });
        }

        // Check for download mode
        const url = new URL(request.url);
        const isDownload = url.searchParams.get('dl') === '1';

        // Handle Range requests (critical for audio/video seeking, especially iOS Safari)
        const rangeHeader = request.headers.get('Range');
        let object;

        if (rangeHeader) {
            // Parse Range header: bytes=start-end
            const match = rangeHeader.match(/bytes=(\d+)-(\d*)/);
            if (match) {
                const offset = parseInt(match[1], 10);
                const end = match[2] ? parseInt(match[2], 10) : undefined;
                const range = end !== undefined
                    ? { offset, length: end - offset + 1 }
                    : { offset };
                object = await env.FILES.get(meta.r2Key, { range });
            } else {
                object = await env.FILES.get(meta.r2Key);
            }
        } else {
            object = await env.FILES.get(meta.r2Key);
        }

        if (!object) {
            return new Response('Not found', { status: 404 });
        }

        // Build response headers
        const headers = new Headers();
        headers.set('Content-Type', meta.contentType || 'application/octet-stream');
        headers.set('Accept-Ranges', 'bytes');
        headers.set('Cache-Control', 'public, max-age=31536000, immutable');
        headers.set('ETag', `"${meta.id}"`);

        if (isDownload) {
            headers.set('Content-Disposition', `attachment; filename="${meta.originalFilename}"`);
            headers.set('Cache-Control', 'no-store');
        }

        // Return partial content for Range requests
        if (rangeHeader && object.range) {
            const { offset } = object.range;
            const length = object.range.length || (meta.size - offset);
            const end = offset + length - 1;
            headers.set('Content-Range', `bytes ${offset}-${end}/${meta.size}`);
            headers.set('Content-Length', String(length));
            return new Response(object.body, { status: 206, headers });
        }

        // Full response
        headers.set('Content-Length', String(meta.size));
        return new Response(object.body, { status: 200, headers });

    } catch (error) {
        return new Response('Server error', { status: 500 });
    }
}
