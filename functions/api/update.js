// Update existing blog post
export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { password, filename, content } = await request.json();

        // Verify password
        if (password !== env.ADMIN_PASSWORD) {
            return new Response(JSON.stringify({ error: 'Invalid password' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Get current file to get SHA
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
        const encodedContent = btoa(unescape(encodeURIComponent(content)));

        // Update file
        const updateResponse = await fetch(
            `https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/posts/${filename}`,
            {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'Cloudflare-Worker'
                },
                body: JSON.stringify({
                    message: `Updated: ${filename}`,
                    content: encodedContent,
                    sha: fileData.sha,
                    branch: 'main'
                })
            }
        );

        if (!updateResponse.ok) {
            return new Response(JSON.stringify({ error: 'Failed to update post' }), {
                status: updateResponse.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify({
            success: true,
            message: 'Post updated successfully'
        }), {
            headers: { 'Content-Type': 'application/json' }
        });

    } catch (error) {
        return new Response(JSON.stringify({ error: 'Update failed' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
