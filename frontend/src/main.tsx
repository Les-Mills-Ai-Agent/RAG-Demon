import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

import { AuthProvider } from 'react-oidc-context';
import { WebStorageStateStore } from 'oidc-client-ts';

const oidcConfig = {
  authority: import.meta.env.VITE_COGNITO_AUTHORITY,   // e.g. https://your-domain.auth.us-east-1.amazoncognito.com use the one in AWS Congnito and set it in your ENV File
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,   // your Cognito App Client ID use the one in AWS Congnito and set it in your ENV File
  redirect_uri: window.location.origin + "/callback",
  post_logout_redirect_uri: window.location.origin + "/",
  response_type: "code",
  scope: "openid email profile",
  automaticSilentRenew: true,
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),

  metadataUrl: "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_nd71G6YgH/.well-known/openid-configuration",
  
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname);
  },
};

const rootElement: HTMLElement | null = document.getElementById('root');

if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      {}
      <AuthProvider {...oidcConfig}>
        <App />
      </AuthProvider>
    </React.StrictMode>
  );
}
