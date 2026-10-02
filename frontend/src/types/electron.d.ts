export {};

declare global {
  interface Window {
    electronAPI?: {
      getConfig: () => Promise<any>;
      saveConfig: (configData: any) => Promise<{ success: boolean; error?: string }>;
      getStatus: () => Promise<{ backendRunning: boolean }>;
      onBackendLog: (callback: (data: string) => void) => void;
      onBackendError: (callback: (data: string) => void) => void;
    };
  }
}
