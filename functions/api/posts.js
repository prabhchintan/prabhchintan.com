// List all blog posts
export async function onRequestGet(context) {
    const { env } = context;

    try {
        const response = await fetch(
            'https://api.github.com/repos/prabhchintan/prabhchintan.com/contents/posts',
            {
                headers: {
                    'Authorization': `token ${env.GITHUB_TOKEN}`,
                    'User-Agent': 'Cloudflare-Worker',
                    'Accept': 'application/vnd.github+json'
                }
            }
        );

        if (!response.ok) {
            return new Response(JSON.stringify({ error: 'Failed to fetch posts' }), {
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const files = await response.json();
        const posts = files
            .filter(f => f.type === 'file' && f.name.endsWith('.md'))
            .map(f => {
                const match = f.name.match(/^(\d{4})_(\d{2})_(\d{2})_(.+)\.md$/);
                if (!match) return null;

                const [, year, month, day, slug] = match;
                return {
                    filename: f.name,
                    slug: slug,
                    date: `${year}-${month}-${day}`,
                    sha: f.sha
                };
            })
            .filter(p => p !== null)
            .sort((a, b) => b.date.localeCompare(a.date));

        return new Response(JSON.stringify({ posts }), {
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
