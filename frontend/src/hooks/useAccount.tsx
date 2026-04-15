import { createContext, useContext, useState, type ReactNode } from 'react';

interface AccountState {
  accountId: string | null;
  accountName: string | null;
  region: string | null;
  email: string | null;
  lastSynced: string | null;
  isConnected: boolean;
  connect: (accountId: string, accountName: string, region: string) => void;
  disconnect: () => void;
  updateEmail: (email: string) => void;
  setLastSynced: (timestamp: string) => void;
}

const AccountContext = createContext<AccountState | null>(null);

const STORAGE_KEY_ID = 'nebula-account-id';
const STORAGE_KEY_NAME = 'nebula-account-name';
const STORAGE_KEY_REGION = 'nebula-account-region';
const STORAGE_KEY_EMAIL = 'nebula-user-email';
const STORAGE_KEY_LAST_SYNCED = 'nebula-last-synced';

export function AccountProvider({ children }: { children: ReactNode }) {
  const [accountId, setAccountId] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_ID) : null
  );
  const [accountName, setAccountName] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_NAME) : null
  );
  const [region, setRegion] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_REGION) : null
  );
  const [email, setEmail] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_EMAIL) : null
  );
  const [lastSynced, setLastSyncedState] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_LAST_SYNCED) : null
  );

  function connect(id: string, name: string, accountRegion: string) {
    localStorage.setItem(STORAGE_KEY_ID, id);
    localStorage.setItem(STORAGE_KEY_NAME, name);
    localStorage.setItem(STORAGE_KEY_REGION, accountRegion);
    setAccountId(id);
    setAccountName(name);
    setRegion(accountRegion);
  }

  function disconnect() {
    localStorage.removeItem(STORAGE_KEY_ID);
    localStorage.removeItem(STORAGE_KEY_NAME);
    localStorage.removeItem(STORAGE_KEY_REGION);
    localStorage.removeItem(STORAGE_KEY_EMAIL);
    localStorage.removeItem(STORAGE_KEY_LAST_SYNCED);
    setAccountId(null);
    setAccountName(null);
    setRegion(null);
    setEmail(null);
    setLastSyncedState(null);
  }

  function updateEmail(newEmail: string) {
    localStorage.setItem(STORAGE_KEY_EMAIL, newEmail);
    setEmail(newEmail);
  }

  function setLastSynced(timestamp: string) {
    localStorage.setItem(STORAGE_KEY_LAST_SYNCED, timestamp);
    setLastSyncedState(timestamp);
  }

  return (
    <AccountContext.Provider
      value={{
        accountId,
        accountName,
        region,
        email,
        lastSynced,
        isConnected: accountId !== null,
        connect,
        disconnect,
        updateEmail,
        setLastSynced,
      }}
    >
      {children}
    </AccountContext.Provider>
  );
}

export function useAccount() {
  const ctx = useContext(AccountContext);
  if (!ctx) throw new Error('useAccount must be used within AccountProvider');
  return ctx;
}
