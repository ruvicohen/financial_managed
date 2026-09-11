import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function LogoutButton() {
  return (
    <form action="/api/logout" method="post">
      <button type="submit" className={cn(buttonVariants({ variant: "outline", size: "sm" }))}>
        Sign out
      </button>
    </form>
  );
}
