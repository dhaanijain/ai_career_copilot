import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-white/[0.06] shimmer",
        className
      )}
    />
  );
}

export function JobCardSkeleton() {
  return (
    <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5 space-y-4">
      <div className="flex gap-4">
        <Skeleton className="w-20 h-20 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </div>
      <div className="space-y-2">
        <Skeleton className="h-3 w-1/4" />
        <div className="flex gap-2">
          <Skeleton className="h-6 w-16 rounded-lg" />
          <Skeleton className="h-6 w-20 rounded-lg" />
          <Skeleton className="h-6 w-14 rounded-lg" />
        </div>
      </div>
      <Skeleton className="h-14 rounded-xl" />
    </div>
  );
}

export function SkillsSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-5 w-32" />
      <div className="flex flex-wrap gap-2">
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton key={i} className="h-7 rounded-lg" style={{ width: `${60 + Math.random() * 60}px` }} />
        ))}
      </div>
    </div>
  );
}
