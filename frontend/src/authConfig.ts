import { WebStorageStateStore } from "oidc-client-ts";

export const oidcConfig = {
  authority: import.meta.env.VITE_COGNITO_AUTHORITY,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirect_uri: `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}/callback`,

  // use sessionStorage so login disappears when browser fully quits
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  automaticSilentRenew: true,  // renew token in background (safe with sessionStorage)
  loadUserInfo: true           // load extra profile claims from the userinfo endpoint
};
