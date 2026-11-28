/* DEPRECATED: this FastAPI browser client is not part of the active archive.
 * The current GitHub Pages release uses assets/js/supabase-archive.js only.
 * Do not load both clients on the same page: they implement incompatible
 * authentication, catalog payloads, and storage paths.
 * Keep this file as a historical prototype until a deployed private API
 * replaces the Supabase REST/Storage adapter through a reviewed migration.
 */
(() => {
  "use strict";
  if (document.currentScript) {
    document.currentScript.dataset.state = "deprecated-not-loaded";
  }
})();
