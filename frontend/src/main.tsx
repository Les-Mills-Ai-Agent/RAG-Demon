import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

import { AuthProvider } from 'react-oidc-context';
import { WebStorageStateStore, InMemoryWebStorage } from 'oidc-client-ts';

// Hosted UI base, e.g. https://<domain>.auth.<region>.amazoncognito.com  (no trailing slash)
const authority = import.meta.env.VITE_COGNITO_AUTHORITY as string;
// Issuer from the IdP (user pool) domain, e.g.
// https://cognito-idp.<region>.amazonaws.com/<userPoolId>
const issuer = import.meta.env.VITE_COGNITO_ISSUER as string;

const oidcConfig = {
  authority,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID as string,
  redirect_uri: window.location.origin + '/callback',
  post_logout_redirect_uri: window.location.origin + '/signed-out',
  response_type: 'code',
  scope: 'openid email profile',

  // Non-persistent auth: no silent renew + in-memory store
  automaticSilentRenew: false,
  userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),

  // Inline metadata to avoid CORS on metadataUrl
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
    window.history.replaceState({}, document.title, window.location.pathname);
  },
};

const rootElement: HTMLElement | null = document.getElementById('root');

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
