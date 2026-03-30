import { NextResponse } from 'next/server';


export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 1200;


function resolveBackendBaseUrl() {
  const candidates = [process.env.INTERNAL_API_URL, process.env.NEXT_PUBLIC_API_URL, 'http://127.0.0.1:8000'];

  for (const candidate of candidates) {
    const value = candidate?.trim();
    if (!value) continue;
    return value.replace(/\/+$/, '').replace(/\/api\/v1$/, '');
  }

  return 'http://127.0.0.1:8000';
}


export async function POST() {
  const backendUrl = `${resolveBackendBaseUrl()}/api/v1/indexing/rebuild-poi`;

  try {
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
      signal: AbortSignal.timeout(20 * 60 * 1000),
    });

    const payload = (await response.json().catch(() => null)) as unknown;
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unable to reach backend rebuild endpoint';
    return NextResponse.json(
      {
        detail: `Indexing proxy failed: ${message}`,
      },
      { status: 502 }
    );
  }
}
