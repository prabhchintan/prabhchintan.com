// Upload media file
const ALLOWED_EXTENSIONS = new Set([
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico', 'avif',
    'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a',
    'mp4', 'webm', 'mov',
    'pdf', 'txt', 'csv', 'json'
]);

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const formData = await request.formData();
        const password = formData.get('password');
        const file = formData.get('file');
        const requestedFilename = formData.get('filename'); // Client can specify exact filename

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

        // Validate file type
        const ext = (file.name.split('.').pop() || '').toLowerCase();
        if (!ALLOWED_EXTENSIONS.has(ext)) {
            return new Response(JSON.stringify({ error: `File type .${ext} is not allowed` }), {
                status: 400,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Use requested filename if provided, otherwise generate one
        let filename;
        if (requestedFilename) {
            filename = requestedFilename;
        } else {
            // Fallback: Generate filename with date prefix
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const timestamp = Date.now();
            const cleanName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_');
            filename = `${year}_${month}_${day}_${timestamp}_${cleanName}`;
        }

        // Read file as base64 (chunked to avoid call stack overflow on large files)
        const arrayBuffer = await file.arrayBuffer();
        const bytes = new Uint8Array(arrayBuffer);
        let binary = '';
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
        }
        const base64 = btoa(binary);

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
            return new Response(JSON.stringify({ error: 'Failed to upload file' }), {
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
        return new Response(JSON.stringify({ error: 'Upload failed' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
