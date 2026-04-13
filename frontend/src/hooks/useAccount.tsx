import { createContext, useContext, useState, type ReactNode } from 'react';

interface AccountState {
  accountId: string | null;
  accountName: string | null;
  isConnected: boolean;
  connect: (accountId: string, accountName: string) => void;
  disconnect: () => void;
}

const AccountContext = createContext<AccountState | null>(null);

const STORAGE_KEY_ID = 'nebula-account-id';
const STORAGE_KEY_NAME = 'nebula-account-name';

export function AccountProvider({ children }: { children: ReactNode }) {
  const [accountId, setAccountId] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_ID) : null
  );
  const [accountName, setAccountName] = useState<string | null>(() =>
    typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY_NAME) : null
  );

  function connect(id: string, name: string) {
    localStorage.setItem(STORAGE_KEY_ID, id);
    localStorage.setItem(STORAGE_KEY_NAME, name);
    setAccountId(id);
    setAccountName(name);
  }

  function disconnect() {
    localStorage.removeItem(STORAGE_KEY_ID);
    localStorage.removeItem(STORAGE_KEY_NAME);
    setAccountId(null);
    setAccountName(null);
  }

  return (
    <AccountContext.Provider
      value={{
        accountId,
        accountName,
        isConnected: accountId !== null,
        connect,
        disconnect,
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
