import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

import { AuthProvider } from "react-oidc-context";
import { WebStorageStateStore } from "oidc-client-ts";

// Hosted UI base, e.g. https://<domain>.auth.<region>.amazoncognito.com  (no trailing slash)
const authority = import.meta.env.VITE_COGNITO_AUTHORITY as string;
// Issuer from the IdP (user pool) domain, e.g.
// https://cognito-idp.<region>.amazonaws.com/<userPoolId>
const issuer = import.meta.env.VITE_COGNITO_ISSUER as string;

const oidcConfig = {
  authority,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID as string,
  redirect_uri: window.location.origin + "/callback",
  post_logout_redirect_uri: window.location.origin + "/signed-out",
  response_type: "code",
  scope: "openid email profile", // adjust as needed

  // Persist session across refreshes (sessionStorage) and renew tokens
  automaticSilentRenew: true,
  userStore: new WebStorageStateStore({ store: window.localStorage }),
  // If you prefer persistence across full browser restarts, use localStorage instead:
  // userStore: new WebStorageStateStore({ store: window.localStorage }),

  // Inline metadata (avoids a fetch to .well-known/openid-configuration)
  metadata: {
    issuer, // IdP issuer
    authorization_endpoint: `${authority}/oauth2/authorize`,
    token_endpoint: `${authority}/oauth2/token`,
    userinfo_endpoint: `${authority}/oauth2/userInfo`,
    end_session_endpoint: `${authority}/logout`,
    revocation_endpoint: `${authority}/oauth2/revoke`,
    jwks_uri: `${issuer}/.well-known/jwks.json`,
  },

  onSigninCallback: () => {
    // Clean up the /callback URL
    window.history.replaceState({}, document.title, window.location.pathname);
    window.history.replaceState({}, document.title, "/home");
  },
};

const rootElement: HTMLElement | null = document.getElementById("root");

if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <AuthProvider {...oidcConfig}>
        <App />
      </AuthProvider>
    </React.StrictMode>
  );
}
