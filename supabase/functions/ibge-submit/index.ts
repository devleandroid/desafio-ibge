import { createClient } from "npm:@supabase/supabase-js@2";
import { parseStatistics } from "./validation.ts";

const CORS_HEADERS = {
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Origin": "*",
};

/** Builds JSON responses with the headers required by browser clients. */
function jsonResponse(body: unknown, status: number): Response {
  return Response.json(body, {
    status,
    headers: CORS_HEADERS,
  });
}

Deno.serve(async (request: Request): Promise<Response> => {
  if (request.method === "OPTIONS") {
    return new Response("ok", { headers: CORS_HEADERS });
  }
  if (request.method !== "POST") {
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  const authorization = request.headers.get("Authorization");
  const tokenMatch = authorization?.match(/^Bearer\s+(\S+)$/i);
  if (!authorization || !tokenMatch) {
    return jsonResponse({ error: "Authentication required" }, 401);
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY");
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error("Supabase URL or anon key is not configured.");
    return jsonResponse({ error: "Service configuration error" }, 500);
  }

  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
    global: {
      headers: { Authorization: authorization },
    },
  });
  const { data: userData, error: authError } = await supabase.auth.getUser(
    tokenMatch[1],
  );
  if (authError || !userData.user) {
    return jsonResponse({ error: "Invalid access token" }, 401);
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Request body must be valid JSON" }, 400);
  }
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return jsonResponse({ error: "Request body must be a JSON object" }, 400);
  }

  const statistics = parseStatistics(
    (body as Record<string, unknown>).stats,
  );
  if (!statistics) {
    return jsonResponse({ error: "Invalid statistics payload" }, 400);
  }

  const { error: insertError } = await supabase
    .from("ibge_statistics")
    .insert({
      user_id: userData.user.id,
      ...statistics,
      stats: statistics,
    });
  if (insertError) {
    console.error("Failed to persist IBGE statistics:", insertError.message);
    return jsonResponse({ error: "Could not save statistics" }, 500);
  }

  return jsonResponse({ success: true }, 201);
});
