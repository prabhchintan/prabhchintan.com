// Delete blog post
export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { password, filename } = await request.json();

        // Verify password
        if (password !== env.ADMIN_PASSWORD) {
            return new Response(JSON.stringify({ error: 'Invalid password' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Get file SHA first
        const getResponse = await fetch(
            `https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/posts/${filename}`,
            {
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'User-Agent': 'Cloudflare-Worker',
                    'Accept': 'application/vnd.github+json'
                }
            }
        );

        if (!getResponse.ok) {
            return new Response(JSON.stringify({ error: 'File not found' }), {
                status: 404,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const fileData = await getResponse.json();

        // Delete file
        const deleteResponse = await fetch(
            `https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/posts/${filename}`,
            {
                method: 'DELETE',
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'Cloudflare-Worker'
                },
                body: JSON.stringify({
                    message: `Deleted: ${filename}`,
                    sha: fileData.sha,
                    branch: 'main'
                })
            }
        );

        if (!deleteResponse.ok) {
            const error = await deleteResponse.json();
            return new Response(JSON.stringify({ error: error.message }), {
                status: deleteResponse.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify({
            success: true,
            message: 'Post deleted successfully'
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
