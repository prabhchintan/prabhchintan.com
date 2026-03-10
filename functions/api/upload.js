// Upload media file
export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const formData = await request.formData();
        const password = formData.get('password');
        const file = formData.get('file');

        // Verify password
        if (password !== env.ADMIN_PASSWORD) {
            return new Response(JSON.stringify({ error: 'Invalid password' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        if (!file) {
            return new Response(JSON.stringify({ error: 'No file provided' }), {
                status: 400,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Generate filename with date prefix
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const timestamp = Date.now();
        const ext = file.name.split('.').pop();
        const cleanName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
        const filename = `${year}_${month}_${day}_${timestamp}_${cleanName}`;

        // Read file as base64
        const arrayBuffer = await file.arrayBuffer();
        const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

        // Upload to GitHub
        const uploadResponse = await fetch(
            `https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/media/${filename}`,
            {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'Cloudflare-Worker'
                },
                body: JSON.stringify({
                    message: `Upload media: ${filename}`,
                    content: base64,
                    branch: 'main'
                })
            }
        );

        if (!uploadResponse.ok) {
            const error = await uploadResponse.json();
            return new Response(JSON.stringify({ error: error.message }), {
                status: uploadResponse.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const result = await uploadResponse.json();

        return new Response(JSON.stringify({
            success: true,
            filename,
            url: `/media/${filename}`,
            markdown: `![${file.name}](/media/${filename})`
        }), {
            headers: { 'Content-Type': 'application/json' }
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
