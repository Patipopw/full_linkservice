export default function DashboardPage() {
  return (
    <div className="flex flex-1 flex-col gap-4 p-4">
      <h1 className="text-2xl font-bold text-black">ยินดีต้อนรับสู่ Dashboard</h1>
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        {/* ตัวอย่าง Card สถิติ */}
        <div className="aspect-video rounded-xl bg-muted/50 p-4 border text-black">สถิติ 1</div>
        <div className="aspect-video rounded-xl bg-muted/50 p-4 border text-black">สถิติ 2</div>
        <div className="aspect-video rounded-xl bg-muted/50 p-4 border text-black">สถิติ 3</div>
      </div>
      <div className="min-h-screen flex-1 rounded-xl bg-muted/50 md:min-h-min p-4 border text-black">
        เนื้อหาหลักจะแสดงตรงนี้...
      </div>
    </div>
  );
}