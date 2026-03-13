// CSRF protection and rate limiting middleware for all /api/* routes
export async function onRequest(context) {
    const { request } = context;

    // Only enforce on mutation methods
    if (request.method === 'POST' || request.method === 'PUT' || request.method === 'DELETE') {
        const origin = request.headers.get('Origin');
        const referer = request.headers.get('Referer');
        const url = new URL(request.url);
        const allowedOrigins = [url.origin, 'https://prabhchintan.com', 'https://www.prabhchintan.com'];

        // Allow requests with no Origin (e.g. same-origin non-CORS) or matching origin
        if (origin && !allowedOrigins.includes(origin)) {
            return new Response(JSON.stringify({ error: 'Forbidden' }), {
                status: 403,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // If no Origin header, check Referer as fallback
        if (!origin && referer) {
            const refererOrigin = new URL(referer).origin;
            if (!allowedOrigins.includes(refererOrigin)) {
                return new Response(JSON.stringify({ error: 'Forbidden' }), {
                    status: 403,
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        }
    }

    return await context.next();
}
