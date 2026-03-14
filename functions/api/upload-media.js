// POST /api/upload-media — upload any file to R2, store metadata in KV, optionally transcribe audio

function json(data, status = 200) {
    return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json' }
    });
}

function getMediaType(contentType) {
    if (contentType.startsWith('image/')) return 'image';
    if (contentType.startsWith('audio/')) return 'audio';
    if (contentType.startsWith('video/')) return 'video';
    return 'document';
}

export async function onRequestPost(context) {
    const { request, env } = context;

    try {
        const formData = await request.formData();
        const password = formData.get('password');
        const file = formData.get('file');
        const mediaId = formData.get('mediaId');

        if (password !== env.ADMIN_PASSWORD) {
            return json({ error: 'Invalid password' }, 401);
        }

        if (!file || !mediaId) {
            return json({ error: 'Missing file or mediaId' }, 400);
        }

        // Validate mediaId format (UUID-like, alphanumeric + hyphens)
        if (!/^[a-zA-Z0-9-]{8,64}$/.test(mediaId)) {
            return json({ error: 'Invalid mediaId format' }, 400);
        }

        if (file.size > 100 * 1024 * 1024) {
            return json({ error: 'File too large. Maximum: 100MB.' }, 400);
        }

        // Determine file properties
        const ext = (file.name.split('.').pop() || 'bin').toLowerCase().replace(/[^a-z0-9]/g, '');
        const contentType = file.type || 'application/octet-stream';
        const mediaType = getMediaType(contentType);

        // R2 key: media/YYYY/MM/DD/{mediaId}.{ext}
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const r2Key = `media/${year}/${month}/${day}/${mediaId}.${ext}`;

        // Read file into buffer (needed for both R2 upload and optional transcription)
        const arrayBuffer = await file.arrayBuffer();

        // Upload to R2
        await env.FILES.put(r2Key, arrayBuffer, {
            httpMetadata: { contentType }
        });

        // Build metadata
        const metadata = {
            id: mediaId,
            r2Key,
            originalFilename: file.name,
            contentType,
            size: file.size,
            mediaType,
            uploadedAt: now.toISOString()
        };

        // Optional: transcribe audio via Workers AI (if AI binding exists)
        let transcription = null;
        if (env.AI && mediaType === 'audio' && file.size < 25 * 1024 * 1024) {
            try {
                const result = await env.AI.run('@cf/openai/whisper', {
                    audio: Array.from(new Uint8Array(arrayBuffer))
                });
                if (result && result.text) {
                    transcription = result.text.trim();
                    metadata.transcription = transcription;
                }
            } catch (e) {
                // Transcription failed — continue without it
            }
        }

        // Store metadata in KV
        await env.COMMENTS.put(`media:${mediaId}`, JSON.stringify(metadata));

        return json({
            success: true,
            id: mediaId,
            url: `/api/media/${mediaId}`,
            mediaType,
            contentType,
            size: file.size,
            transcription
        });

    } catch (error) {
        return json({ error: 'Upload failed: ' + error.message }, 500);
    }
}
