"use client"

import React, { useEffect, useState } from "react"
import { getQuotations } from "@/services/quotation.service"
import { QuotationResponse } from "@/types/quotation"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Plus, Eye, FileText } from "lucide-react"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"

export default function QuotationListPage() {
  const [quotations, setQuotations] = useState<QuotationResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const fetchData = async () => {
      try {
        const data = await getQuotations()
        setQuotations(data)
      } catch (error) {
        console.error("Fetch error:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // ฟังก์ชันช่วยเลือกสีสถานะ
  const getStatusStyle = (status: string = "draft") => {
    switch (status.toLowerCase()) {
      case "win": return "bg-green-100 text-green-700 hover:bg-green-100 border-green-200"
      case "lost": return "bg-red-100 text-red-700 hover:bg-red-100 border-red-200"
      case "quotation": return "bg-blue-100 text-blue-700 hover:bg-blue-100 border-blue-200"
      case "cancelled": return "bg-gray-100 text-gray-700 hover:bg-gray-100 border-gray-200"
      default: return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100 border-yellow-200"
    }
  }

  if (!mounted) return null // ไม่เรนเดอร์จนกว่าจะอยู่บน Client

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">รายการใบเสนอราคา</h2>
        <Link href="/sale/quotation/create">
          <Button className="flex items-center gap-2">
            <Plus size={18} /> สร้างใบเสนอราคา
          </Button>
        </Link>
      </div>

      <div className="bg-white rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-32">เลขที่ใบเสนอราคา</TableHead>
              <TableHead>ชื่อบริษัท</TableHead>
              <TableHead>ชื่อลูกค้า</TableHead>
              <TableHead className="text-right">ยอดรวมสุทธิ</TableHead>
              <TableHead className="text-center">สถานะ</TableHead>
              <TableHead className="text-center">ผู้สร้าง</TableHead>
              <TableHead className="text-right">จัดการ</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={7} className="text-center py-10">กำลังโหลดข้อมูล...</TableCell></TableRow>
            ) : quotations.length === 0 ? (
              <TableRow><TableCell colSpan={7} className="text-center py-10">ไม่พบข้อมูลใบเสนอราคา</TableCell></TableRow>
            ) : (
              quotations.map((qt) => (
                <TableRow key={qt.id}>
                  <TableCell className="font-medium">{qt.quotation_no}</TableCell>
                  <TableCell>{qt.company_name}</TableCell>
                  <TableCell>{qt.customer_name}</TableCell>
                  <TableCell className="text-right font-semibold">
                    {Number(qt.total_amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge variant="outline" className={`capitalize font-semibold ${getStatusStyle(qt.status)}`}>
                      {qt.status || "draft"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center text-sm text-muted-foreground">{qt.creator}</TableCell>
                  <TableCell className="text-right space-x-2">
                    <Link href={`/sale/quotation/${qt.id}`}>
                      <Button variant="ghost" size="icon" title="ดูรายละเอียด">
                        <Eye size={18} />
                      </Button>
                    </Link>
                    <Button variant="ghost" size="icon" title="พิมพ์ PDF" className="text-blue-600">
                      <FileText size={18} />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
