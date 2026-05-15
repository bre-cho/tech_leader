import GoogleAccountsManager from "@/components/settings/GoogleAccountsManager";

export default function AccountsPage() {
  return (
    <main className="brain-route-main">
      <div className="brain-route-wrap">
        <section className="brain-route-head">
          <p className="brain-route-kicker">Account Center</p>
          <h1 className="brain-route-title">Google Accounts Management</h1>
          <p className="brain-route-desc">
            Quản lý tài khoản Google kết nối với hệ thống, trạng thái hoạt động và quyền dùng theo workspace.
          </p>
        </section>
        <GoogleAccountsManager />
      </div>
    </main>
  );
}
