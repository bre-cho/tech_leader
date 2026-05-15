import Link from "next/link";

const cards = [
  ["Beauty Commerce", "/beauty-commerce", "Chạy luồng bán hàng hình ảnh: nhân vật, sản phẩm, provider và kiểm định."],
  ["Beauty Avatar", "/beauty-avatar", "Tạo avatar KOL nhất quán cho chiến dịch thương mại và video."],
  ["Storyboard V31", "/storyboard-v31", "Dựng phân cảnh theo nhịp giữ chân người xem và cấu trúc video."],
  ["HiDream Commercial", "/hidream-commercial", "Tạo ảnh quảng cáo thương mại cao cấp từ mô tả sản phẩm."],
  ["Color Intelligence", "/color-intelligence", "Phân tích màu sắc, cảm xúc thị giác và nhận diện thương hiệu."],
  ["Video Render Studio", "/video-render", "Render ảnh tĩnh hoặc text prompt thành video với Veo 3.1."],
  ["AI Engine Settings", "/settings/ai-engine", "Quản lý provider, model, khóa API và chính sách định tuyến."],
];

export default function HomePage() {
  return (
    <main className="brain-page-stack">
      <section className="brain-hero-card">
        <p className="brain-eyebrow">Architecture Control Tower</p>
        <h2>Trung tâm điều phối Agent16</h2>
        <p>
          Bản này đã áp dụng bố cục giao diện từ brain-main: nền tối, sidebar điều phối, card kính mờ,
          trạng thái vận hành và luồng kiểm định trước phát hành.
        </p>
      </section>

      <section className="brain-card-grid">
        {cards.map(([title, href, desc]) => (
          <Link key={href} href={href} className="brain-card-link">
            <strong>{title}</strong>
            <span>{desc}</span>
          </Link>
        ))}
      </section>

      <section className="brain-panel-grid">
        <div className="brain-panel">
          <p className="brain-eyebrow">Release Gate</p>
          <h3>Quy trình kiểm duyệt</h3>
          <p>CodeGraph Snapshot → Blast Radius Diff → Architecture Drift Check → Promotion Gate.</p>
        </div>
        <div className="brain-panel">
          <p className="brain-eyebrow">Memory</p>
          <h3>Trí nhớ tổ chức</h3>
          <p>Lưu dấu quyết định, bản vá, hợp đồng bàn giao agent và báo cáo kiểm định.</p>
        </div>
      </section>
    </main>
  );
}
