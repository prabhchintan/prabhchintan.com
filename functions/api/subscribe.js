function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

export async function onRequestGet(context) {
    const { request, env } = context;
    const url = new URL(request.url);

    if (!url.searchParams.has('list')) {
        return json({ error: 'Invalid request' }, 400);
    }

    const password = url.searchParams.get('password');
    if (password !== env.ADMIN_PASSWORD) {
        return json({ error: 'Unauthorized' }, 401);
    }

    try {
        const list = await env.COMMENTS.get('subscribers:list', 'json') || [];
        return json({ subscribers: list, count: list.length });
    } catch (e) {
        return json({ error: 'Server error' }, 500);
    }
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { email, url, remove } = await request.json();

        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 253) {
            return json({ error: 'Invalid email' }, 400);
        }

        if (url) {
            return json({ subscribed: true });
        }

        const list = await env.COMMENTS.get('subscribers:list', 'json') || [];

        if (remove) {
            const filtered = list.filter(s => s.email.toLowerCase() !== email.toLowerCase());
            await env.COMMENTS.put('subscribers:list', JSON.stringify(filtered));
            return json({ removed: true });
        }

        if (list.some(s => s.email.toLowerCase() === email.toLowerCase())) {
            return json({ subscribed: true, already: true });
        }

        list.push({ email, ts: Date.now() });
        await env.COMMENTS.put('subscribers:list', JSON.stringify(list));
        return json({ subscribed: true });
    } catch (e) {
        return json({ error: 'Server error' }, 500);
    }
}
