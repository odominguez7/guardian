// Firebase Auth wiring. Reads config from NEXT_PUBLIC_FIREBASE_* env vars.
// When config is missing (e.g., during initial autonomous bootstrap before
// Omar adds his Firebase project credentials), we degrade gracefully to an
// "anonymous demo" mode rather than crashing.

import type { FirebaseApp } from "firebase/app";
import type { Auth, User } from "firebase/auth";

interface FirebaseClient {
  app: FirebaseApp | null;
  auth: Auth | null;
  configured: boolean;
}

let _client: FirebaseClient | null = null;

export async function getFirebase(): Promise<FirebaseClient> {
  if (_client) return _client;

  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  };

  const allPresent = Object.values(config).every(Boolean);
  if (!allPresent) {
    _client = { app: null, auth: null, configured: false };
    return _client;
  }

  const { initializeApp, getApps, getApp } = await import("firebase/app");
  const { getAuth } = await import("firebase/auth");

  const app = getApps().length ? getApp() : initializeApp(config);
  const auth = getAuth(app);
  _client = { app, auth, configured: true };
  return _client;
}

export async function signInWithGoogle(): Promise<User | null> {
  const { auth } = await getFirebase();
  if (!auth) return null;
  const { GoogleAuthProvider, signInWithPopup } = await import("firebase/auth");
  const provider = new GoogleAuthProvider();
  const result = await signInWithPopup(auth, provider);
  return result.user;
}

export async function signOutUser(): Promise<void> {
  const { auth } = await getFirebase();
  if (!auth) return;
  const { signOut } = await import("firebase/auth");
  await signOut(auth);
}
