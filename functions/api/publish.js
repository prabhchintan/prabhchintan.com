// Create new blog post
export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const { password, title, content, slug, media } = await request.json();

        // Verify password
        if (password !== env.ADMIN_PASSWORD) {
            return new Response(JSON.stringify({ error: 'Invalid password' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Generate filename
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');

        let finalSlug = slug || title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
        if (!slug) {
            const time = String(now.getHours()).padStart(2, '0') + String(now.getMinutes()).padStart(2, '0');
            finalSlug = `${finalSlug}-${time}`;
        }

        const filename = `${year}_${month}_${day}_${finalSlug}.md`;

        // Process content - auto-embed URLs
        let processedContent = content;

        // Build markdown
        const markdown = `# ${title}\n\n${processedContent}`;
        const encodedContent = btoa(unescape(encodeURIComponent(markdown)));

        // Create file via GitHub API
        const response = await fetch(
            `https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/posts/${filename}`,
            {
                method: 'PUT',
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'Cloudflare-Worker'
                },
                body: JSON.stringify({
                    message: `Published: ${title}`,
                    content: encodedContent,
                    branch: 'main'
                })
            }
        );

        if (!response.ok) {
            const error = await response.json();
            return new Response(JSON.stringify({ error: error.message }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        return new Response(JSON.stringify({
            success: true,
            filename,
            message: 'Post published successfully'
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
