import "./globals.css";
import BrainShell from "@/components/BrainShell";

export const metadata = {
  title: "AI Technical Lead Operating System",
  description: "Bang dieu khien Agent16 theo layout Brain Console",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <BrainShell>{children}</BrainShell>
      </body>
    </html>
  );
}
