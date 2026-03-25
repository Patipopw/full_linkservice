"use client"

import React, { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { getQuotationById } from "@/services/quotation.service"
import { QuotationResponse } from "@/types/quotation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Printer, FileEdit, Calendar, User, Building2 } from "lucide-react"

export default function QuotationDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [quotation, setQuotation] = useState<QuotationResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      getQuotationById(params.id as string)
        .then(setQuotation)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [params.id])

  if (loading) return <div className="p-10 text-center animate-pulse">กำลังโหลดข้อมูล...</div>
  if (!quotation) return <div className="p-10 text-center text-destructive">ไม่พบข้อมูลใบเสนอราคา</div>

  return (
    <div className="p-4 md:p-8 space-y-6 max-w-6xl mx-auto">
      {/* Action Bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()} className="hover:bg-accent">
          <ArrowLeft className="mr-2 h-4 w-4" /> ย้อนกลับ
        </Button>
        <div className="flex gap-2 w-full sm:w-auto">
          <Button variant="outline" className="flex-1 sm:flex-none border-blue-200 text-blue-600 hover:bg-blue-50">
            <Printer className="mr-2 h-4 w-4" /> พิมพ์ PDF
          </Button>
          <Button variant="outline" className="flex-1 sm:flex-none">
            <FileEdit className="mr-2 h-4 w-4" /> แก้ไข
          </Button>
        </div>
      </div>

      <Card className="border-none shadow-lg">
        <CardHeader className="bg-slate-50/50 pb-8 border-b">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CardTitle className="text-3xl font-black tracking-tighter text-slate-900">
                  {quotation.quotation_no}
                </CardTitle>
                <Badge className="bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-100 font-bold uppercase">
                  {quotation.status}
                </Badge>
              </div>
              <CardDescription className="flex items-center gap-2 font-medium">
                <Calendar className="h-4 w-4" /> 
                วันที่เสนอราคา: {new Date(quotation.quotation_date).toLocaleDateString('th-TH')}
              </CardDescription>
            </div>
            <div className="text-left md:text-right space-y-1">
              <p className="text-sm font-semibold text-slate-500 uppercase tracking-widest">Project Name</p>
              <p className="text-lg font-bold text-slate-900">{quotation.project_name || "-"}</p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-8">
          {/* Info Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-900 font-bold border-b pb-2">
                <Building2 className="h-4 w-4 text-blue-600" />
                ข้อมูลลูกค้า / บริษัท
              </div>
              <div className="space-y-1 pl-6">
                <p className="font-bold text-xl text-slate-800">{quotation.company_name}</p>
                <p className="text-sm text-slate-500 leading-relaxed whitespace-pre-wrap">{quotation.company_address}</p>
                <Separator className="my-2" />
                <p className="text-sm"><b>ชื่อผู้ติดต่อ:</b> {quotation.customer_name}</p>
                <p className="text-sm"><b>โทรศัพท์:</b> {quotation.customer_tel || "-"}</p>
                <p className="text-sm"><b>อีเมล:</b> {quotation.customer_email || "-"}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-900 font-bold border-b pb-2">
                <User className="h-4 w-4 text-blue-600" />
                พนักงานขาย / ผู้ดูแล
              </div>
              <div className="space-y-1 pl-6">
                <p className="font-bold text-lg text-slate-800">{quotation.sale_name}</p>
                <p className="text-sm"><b>รหัสพนักงาน:</b> {quotation.sale_id}</p>
                <p className="text-sm"><b>อีเมล:</b> {quotation.sale_email || "-"}</p>
                <Separator className="my-2" />
                <p className="text-sm text-slate-500">
                  ยืนยันราคาถึงวันที่ (Validity Date): 
                  <span className="ml-2 font-bold text-slate-800">
                    {new Date(quotation.validity_date).toLocaleDateString('th-TH')}
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* Items Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader className="bg-slate-50">
                <TableRow>
                  <TableHead className="w-12.5] text-center">#</TableHead>
                  <TableHead>รายละเอียดสินค้า / บริการ</TableHead>
                  <TableHead className="w-25 text-center">จำนวน</TableHead>
                  <TableHead className="w-37.5 text-right">ราคา/หน่วย</TableHead>
                  <TableHead className="w-37.5 text-right font-bold">รวมเงิน</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quotation.items.map((item, idx) => (
                  <TableRow key={item.id} className="hover:bg-slate-50/50">
                    <TableCell className="text-center text-slate-500 font-mono">{idx + 1}</TableCell>
                    <TableCell>
                      <div className="font-semibold text-slate-800">{item.product_name || "ไม่มีชื่อสินค้า"}</div>
                      <div className="text-sm text-slate-500 whitespace-pre-wrap">{item.product_description}</div>
                      {item.red_note && <p className="text-red-500 text-xs font-bold mt-1">** {item.red_note}</p>}
                    </TableCell>
                    <TableCell className="text-center font-medium">
                      {Number(item.quantity).toLocaleString()} {item.unit || "ชิ้น"}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {new Intl.NumberFormat('th-TH', { minimumFractionDigits: 2 }).format(Number(item.price))}
                    </TableCell>
                    <TableCell className="text-right font-bold font-mono">
                      {new Intl.NumberFormat('th-TH', { minimumFractionDigits: 2 }).format(Number(item.total_item_price))}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Footer Totals */}
          <div className="flex flex-col items-end mt-8 space-y-2">
            <div className="flex justify-between w-full md:w-80 px-4 py-2 bg-slate-50 rounded-lg">
              <span className="font-semibold text-slate-500">ราคารวม (Subtotal)</span>
              <span className="font-bold text-slate-800">
                {new Intl.NumberFormat('th-TH', { minimumFractionDigits: 2 }).format(Number(quotation.total_amount))}
              </span>
            </div>
            <div className="flex justify-between w-full md:w-80 px-4 py-3 bg-blue-600 rounded-lg shadow-md">
              <span className="font-bold text-white uppercase tracking-wider">ยอดรวมสุทธิ</span>
              <span className="font-black text-white text-xl">
                {new Intl.NumberFormat('th-TH', { minimumFractionDigits: 2 }).format(Number(quotation.total_amount))} บาท
              </span>
            </div>
            <p className="text-[10px] text-slate-400 italic mt-2">บันทึกโดย: {quotation.creator} ({new Date(quotation.created_at).toLocaleString('th-TH')})</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
