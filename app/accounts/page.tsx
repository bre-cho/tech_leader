import GoogleAccountsManager from "@/components/settings/GoogleAccountsManager";

export default function AccountsPage() {
  return (
    <main className="min-h-screen bg-neutral-950 p-8 text-white">
      <div className="mx-auto max-w-6xl">
        <GoogleAccountsManager />
      </div>
    </main>
  );
}
