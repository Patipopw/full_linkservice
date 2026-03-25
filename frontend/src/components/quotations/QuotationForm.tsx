"use client"

import React, { useEffect } from "react"
import { useForm, useFieldArray, useWatch, FormProvider } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Plus, Trash2, Save } from "lucide-react"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Field,
  FieldLabel,
} from "@/components/ui/field"

import { createQuotation } from "@/services/quotation.service"
import { QuotationCreate } from "@/types/quotation"
import Cookies from "js-cookie"

const formSchema = z.object({
  company_name: z.string().min(1, "กรุณากรอกชื่อบริษัท"),
  company_address: z.string().optional(),
  customer_name: z.string().min(1, "กรุณากรอกชื่อลูกค้า"),
  customer_tel: z.string().optional(),
  customer_email: z.string().email("อีเมลไม่ถูกต้อง").or(z.literal("")).optional(),
  quotation_date: z.string(),
  validity_date: z.string(),
  sale_name: z.string().min(1, "กรุณากรอกชื่อพนักงานขาย"),
  sale_email: z.string().email().optional(),
  sale_id: z.string().min(1, "กรุณากรอกรหัสพนักงาน"),
  project_name: z.string().optional(),
  status: z.string(),
  version: z.number(),
  items: z.array(z.object({
    product_description: z.string().min(1, "กรุณากรอกรายละเอียด"),
    quantity: z.number().min(1),
    price: z.number().min(0),
    cost: z.number() // ใส่เป็น number ปกติ (ไม่ใช้ .default) เพื่อแก้ปัญหา Type Error
  }))
})

type FormValues = z.infer<typeof formSchema>

export default function QuotationForm() {
  const router = useRouter()
  const methods = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      status: "draft",
      version: 0,
      company_name: "",
      company_address: "",
      customer_name: "",
      customer_tel: "",
      customer_email: "",
      quotation_date: new Date().toISOString().split('T')[0],
      validity_date: "",
      sale_name: "",
      sale_id: "",
      project_name: "",
      items: [{
        product_description: "",
        quantity: 1,
        price: 0,
        cost: 0
      }]
    }
  })

  const { reset, getValues } = methods;

  useEffect(() => {
  // ดึงค่าจาก Cookies ตรงๆ
  console.log(Cookies)
  const fullName = Cookies.get("user_full_name") // ต้องมั่นใจว่าตอน Login เก็บชื่อนี้ไว้
  const userId = Cookies.get("user_id")
  const email = Cookies.get("user_email")

  if (fullName || userId) {
    reset({
      ...getValues(),
      sale_name: fullName || email || "",
      sale_id: userId || "",
      sale_email: email || ""
    })
  }
}, [reset, getValues])


  
  const { fields, append, remove } = useFieldArray({
    control: methods.control,
    name: "items"
  })

  // 2. ใช้ useWatch คำนวณราคารวม (Real-time)
  const watchItems = useWatch({ control: methods.control, name: "items" })
  const totalAmount = (watchItems || []).reduce(
    (acc, item) => acc + ((Number(item?.quantity) || 0) * (Number(item?.price) || 0)),
    0
  )

  const onSubmit = async (values: FormValues) => {
    try {
      const payload: QuotationCreate = {
        ...values,
        sale_name: "System Admin", // ดึงจาก User Context ในอนาคต
        sale_id: "S001",
        total_amount: totalAmount,
        items: values.items.map((item, idx) => ({
          ...item,
          item_no: idx + 1,
          total_item_price: item.quantity * item.price
        }))
      }

      const result = await createQuotation(payload)
      alert(`สร้างใบเสนอราคา ${result.quotation_no} สำเร็จ!`)
      router.push("/sale/quotation")
      router.refresh()
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "เกิดข้อผิดพลาด"
      alert(message)
    }
  }

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)} className="space-y-6">
        <Card>
          <CardHeader><CardTitle>ข้อมูลทั่วไป</CardTitle></CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Field>
              <FieldLabel>ชื่อบริษัท</FieldLabel>
              <Input {...methods.register("company_name")} />
              {methods.formState.errors.company_name && <span className="text-xs text-destructive">{methods.formState.errors.company_name.message}</span>}
            </Field>
            <Field>
              <FieldLabel>ชื่อโครงการ (Project)</FieldLabel>
              <Input {...methods.register("project_name")} />
            </Field>

            {/* แถวที่ 2: ที่อยู่ (ใช้เต็มบรรทัด) */}
            <div className="md:col-span-2">
              <Field>
                <FieldLabel>ที่อยู่บริษัท</FieldLabel>
                <Textarea {...methods.register("company_address")} rows={2} />
              </Field>
            </div>

            {/* แถวที่ 3 */}
            <Field>
              <FieldLabel>ชื่อผู้ติดต่อ (Customer)</FieldLabel>
              <Input {...methods.register("customer_name")} />
            </Field>
            <Field>
              <FieldLabel>เบอร์โทรศัพท์ลูกค้า</FieldLabel>
              <Input {...methods.register("customer_tel")} />
            </Field>

            {/* แถวที่ 4 */}
            <Field>
              <FieldLabel>วันที่เสนอราคา</FieldLabel>
              <Input type="date" {...methods.register("quotation_date")} />
            </Field>
            <Field>
              <FieldLabel>ยืนยันราคาถึงวันที่</FieldLabel>
              <Input type="date" {...methods.register("validity_date")} />
            </Field>

            {/* แถวที่ 5: ข้อมูลผู้ขาย */}
            <Field>
              <FieldLabel>ชื่อพนักงานขาย (Sale)</FieldLabel>
              <Input {...methods.register("sale_name")} />
            </Field>
            <Field>
              <FieldLabel>รหัสพนักงานขาย</FieldLabel>
              <Input {...methods.register("sale_id")} />
            </Field>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>รายการสินค้า</CardTitle>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => append({ product_description: "", quantity: 1, price: 0, cost: 0 })}
            >
              <Plus className="mr-2 h-4 w-4" /> เพิ่มรายการ
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>รายละเอียดสินค้า</TableHead>
                  <TableHead className="w-24 text-center">จำนวน</TableHead>
                  <TableHead className="w-32 text-right">ราคาต่อหน่วย</TableHead>
                  <TableHead className="w-32 text-right">รวม</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fields.map((field, index) => (
                  <TableRow key={field.id}>
                    <TableCell>
                      <Field>
                        <Textarea
                          {...methods.register(`items.${index}.product_description` as const)}
                          rows={1}
                          className="min-h-10 resize-none"
                        />
                      </Field>
                    </TableCell>
                    <TableCell>
                      <Field>
                        <Input
                          type="number"
                          {...methods.register(`items.${index}.quantity` as const, { valueAsNumber: true })}
                          className="text-center"
                        />
                      </Field>
                    </TableCell>
                    <TableCell>
                      <Field>
                        <Input
                          type="number"
                          {...methods.register(`items.${index}.price` as const, { valueAsNumber: true })}
                          className="text-right"
                        />
                      </Field>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {((watchItems[index]?.quantity || 0) * (watchItems[index]?.price || 0)).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell>
                      <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="mt-6 flex flex-col items-end gap-2 border-t pt-4">
              <div className="text-sm text-muted-foreground">ยอดรวมสุทธิ (Grand Total)</div>
              <div className="text-3xl font-bold text-primary">
                {totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })} <span className="text-sm">บาท</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Button type="submit" className="w-full h-12 text-lg font-bold">
          <Save className="mr-2 h-5 w-5" /> บันทึกและออกใบเสนอราคา
        </Button>
      </form>
    </FormProvider>
  )
}
