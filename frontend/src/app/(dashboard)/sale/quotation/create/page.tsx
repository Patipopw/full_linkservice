import QuotationForm from "@/components/quotations/QuotationForm"

export default function CreateQuotationPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">สร้างใบเสนอราคาใหม่</h2>
      </div>
      <div className="grid gap-4">
        {/* นำ Form ที่เราสร้างไว้มาวางตรงนี้ */}
        <QuotationForm />
      </div>
    </div>
  )
}