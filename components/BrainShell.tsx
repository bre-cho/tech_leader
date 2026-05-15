"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

type NavItem = {
  label: string;
  href: string;
  desc: string;
  badge?: string;
};

const navItems: NavItem[] = [
  { label: "Tổng quan", href: "/", desc: "Trung tâm điều phối AI Technical Lead", badge: "Home" },
  { label: "Beauty Commerce", href: "/beauty-commerce", desc: "Luồng bán hàng hình ảnh K-beauty", badge: "V28" },
  { label: "Beauty Commerce V28", href: "/beauty-commerce-v28", desc: "Điều phối avatar, sản phẩm và kiểm định", badge: "Run" },
  { label: "Beauty Intelligence", href: "/beauty-intelligence", desc: "Phân tích nhận thức khuôn mặt và thương mại", badge: "AI" },
  { label: "Beauty Avatar", href: "/beauty-avatar", desc: "Xây nhân vật KOL nhất quán", badge: "8K" },
  { label: "Storyboard V31", href: "/storyboard-v31", desc: "Nhịp giữ chân người xem và cảnh quay", badge: "New" },
  { label: "Storyboard V30", href: "/storyboard-v30", desc: "Máy dựng phân cảnh chuyển đổi", badge: "Flow" },
  { label: "HiDream Commercial", href: "/hidream-commercial", desc: "Tạo ảnh thương mại cao cấp", badge: "Img" },
  { label: "Color Intelligence", href: "/color-intelligence", desc: "Bản đồ màu sắc, nhận diện và cảm xúc", badge: "UI" },
  { label: "Cài đặt AI Engine", href: "/settings/ai-engine", desc: "Quản lý provider, khóa API và định tuyến", badge: "Ops" },
];

export default function BrainShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="brain-shell">
      <aside className="brain-sidebar">
        <div className="brain-brand">
          <p className="brain-eyebrow">Agent16 Operating System</p>
          <h2>AI Technical Lead Console</h2>
          <p>
            Giao diện điều phối theo phong cách Brain: tối giản, kính mờ, ưu tiên luồng vận hành và kiểm duyệt.
          </p>
        </div>

        <nav className="brain-nav" aria-label="Điều hướng chính">
          {navItems.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link key={item.href} href={item.href} className={`brain-nav-item ${active ? "active" : ""}`}>
                <span>
                  <strong>{item.label}</strong>
                  <small>{item.desc}</small>
                </span>
                <em>{active ? "Mở" : item.badge ?? "Go"}</em>
              </Link>
            );
          })}
        </nav>

        <div className="brain-workflow-card">
          <p className="brain-eyebrow">Core Workflow</p>
          <ol>
            <li>Nhận yêu cầu</li>
            <li>Quét kiến trúc</li>
            <li>Lập kế hoạch vá</li>
            <li>Thực thi có kiểm soát</li>
            <li>Kiểm định trước phát hành</li>
          </ol>
        </div>
      </aside>

      <section className="brain-content">
        <div className="brain-topbar">
          <div>
            <p className="brain-eyebrow">Production Control Plane</p>
            <h1>Tech Leader MVP</h1>
          </div>
          <div className="brain-status-pill">Layout copied from brain-main</div>
        </div>
        {children}
      </section>
    </div>
  );
}
