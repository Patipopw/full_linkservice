"use client"

import { AppSidebar } from "@/components/app-sidebar"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Separator } from "@/components/ui/separator"
import { usePathname } from "next/navigation"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import React from "react"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  
  // แปลง Pathname เป็น Array เช่น "/dashboard/sale" -> ["dashboard", "sale"]
  const pathSegments = pathname.split('/').filter(segment => segment !== "")

  // ฟังก์ชันช่วยเปลี่ยนชื่อภาษาอังกฤษเป็นภาษาไทย (Optional)
  const getThaiName = (name: string) => {
    const map: Record<string, string> = {
      dashboard: "Dashboard",
      sale: "Sale",
      profile: "ข้อมูลส่วนตัว",
    }
    return map[name] || name.charAt(0).toUpperCase() + name.slice(1)
  }

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        
        <SidebarInset>
          <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear border-b px-4">
            <div className="flex items-center gap-2">
              <SidebarTrigger className="-ml-1" />
              <Separator orientation="vertical" className="mr-2 h-4" />
              
              {/* --- เริ่มต้น Breadcrumb --- */}
              <Breadcrumb>
                <BreadcrumbList>
                  {pathSegments.map((segment, index) => {
                    const href = `/${pathSegments.slice(0, index + 1).join('/')}`
                    const isLast = index === pathSegments.length - 1

                    return (
                      <React.Fragment key={href}>
                        <BreadcrumbItem>
                          {isLast ? (
                            <BreadcrumbPage className="text-black font-medium">
                              {getThaiName(segment)}
                            </BreadcrumbPage>
                          ) : (
                            <BreadcrumbLink href={href} className="hover:text-blue-600 transition-colors">
                              {getThaiName(segment)}
                            </BreadcrumbLink>
                          )}
                        </BreadcrumbItem>
                        {!isLast && <BreadcrumbSeparator />}
                      </React.Fragment>
                    )
                  })}
                </BreadcrumbList>
              </Breadcrumb>
              {/* --- สิ้นสุด Breadcrumb --- */}
            </div>
          </header>
          
          <main className="flex flex-1 flex-col gap-4 p-4">
            {children}
          </main>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}