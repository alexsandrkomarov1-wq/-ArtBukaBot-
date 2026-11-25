const ALLOWED_ORIGIN = "https://alexsandrkomarov1-wq.github.io";

function corsHeaders(origin) {
  const headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Vary": "Origin"
  };
  if (origin === ALLOWED_ORIGIN) {
    headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN;
    headers["Access-Control-Allow-Methods"] = "GET, OPTIONS";
    headers["Access-Control-Allow-Headers"] = "Accept, Content-Type";
    headers["Access-Control-Max-Age"] = "600";
  }
  return headers;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const headers = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      if (origin && origin !== ALLOWED_ORIGIN) {
        return new Response(null, { status: 403 });
      }
      return new Response(null, { status: 204, headers });
    }

    if (request.method !== "GET") {
      return Response.json({ ok: false, error: "Method not allowed" }, { status: 405, headers: { ...headers, Allow: "GET, OPTIONS" } });
    }

    if (url.pathname !== "/" && url.pathname !== "/status") {
      return Response.json({ ok: false, error: "Not found" }, { status: 404, headers });
    }

    const baseUrl = process.env.NEON_AI_GATEWAY_BASE_URL;
    const token = process.env.NEON_AI_GATEWAY_TOKEN;
    if (!baseUrl || !token) {
      return Response.json({
        ok: false,
        gateway_connected: false,
        model_access: "unknown",
        error: "Neon AI Gateway environment is not available in this Function"
      }, { status: 503, headers });
    }

    try {
      const response = await fetch(baseUrl.replace(/\/$/, "") + "/v1/models", {
        method: "GET",
        headers: { Authorization: "Bearer " + token, Accept: "application/json" }
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || !Array.isArray(payload.data)) {
        return Response.json({
          ok: false,
          gateway_connected: false,
          model_access: "unknown",
          gateway_status: response.status
        }, { status: 502, headers });
      }

      const total = payload.data.length;
      const enabled = payload.data.filter((model) => model.enabled === true).length;
      const reasons = [...new Set(payload.data.map((model) => model.unavailable_reason).filter(Boolean))];
      const modelAccess = enabled > 0 ? "ready" : reasons.includes("paid_plan_required") ? "credits_required" : "unknown";

      return Response.json({
        ok: true,
        gateway_connected: true,
        model_access: modelAccess,
        enabled_model_count: enabled,
        total_model_count: total,
        reason: modelAccess === "credits_required" ? "paid_plan_required" : null,
        checked_at: new Date().toISOString()
      }, { status: 200, headers });
    } catch (_) {
      return Response.json({
        ok: false,
        gateway_connected: false,
        model_access: "unknown",
        error: "Could not reach Neon AI Gateway"
      }, { status: 502, headers });
    }
  }
};
