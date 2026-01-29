import { useState } from "react";
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";
import { Id } from "../convex/_generated/dataModel";
import { cn } from "./lib/utils";
import { useTheme } from "./lib/theme";
import { Badge, getBadgeVariant } from "./components/ui/badge";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogClose,
} from "./components/ui/dialog";

// ============ Theme Toggle ============
function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Select value={theme} onValueChange={(value) => setTheme(value as "light" | "dark" | "system")}>
      <SelectTrigger className="w-32">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="light">
          <span className="flex items-center gap-2">
            <svg className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            Light
          </span>
        </SelectItem>
        <SelectItem value="dark">
          <span className="flex items-center gap-2">
            <svg className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            Dark
          </span>
        </SelectItem>
        <SelectItem value="system">
          <span className="flex items-center gap-2">
            <svg className="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            System
          </span>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}

export default function App() {
  const [selectedCompanyId, setSelectedCompanyId] =
    useState<Id<"companies"> | null>(null);

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="flex items-center justify-between border-b border-neutral-200 bg-white px-6 py-3 dark:border-neutral-800 dark:bg-neutral-900">
        <div className="flex items-center gap-3">
          <div className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600">
            <svg className="size-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-semibold text-neutral-900 dark:text-neutral-100">
              Signal
            </h1>
            <p className="text-xs text-neutral-500">Sales Pipeline Dashboard</p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 p-6">
        <Tabs defaultValue="companies">
          <TabsList>
            <TabsTrigger value="companies">Companies</TabsTrigger>
            <TabsTrigger value="contacts">Contacts</TabsTrigger>
            <TabsTrigger value="outreach">Outreach</TabsTrigger>
          </TabsList>

          <TabsContent value="companies">
            <CompaniesView onSelectCompany={setSelectedCompanyId} />
          </TabsContent>

          <TabsContent value="contacts">
            <ContactsView />
          </TabsContent>

          <TabsContent value="outreach">
            <OutreachView />
          </TabsContent>
        </Tabs>
      </main>

      <CompanyModal
        companyId={selectedCompanyId}
        onClose={() => setSelectedCompanyId(null)}
      />
    </div>
  );
}

// ============ Stats Card ============
function StatCard({
  label,
  value,
  variant = "default",
}: {
  label: string;
  value: number | string;
  variant?: "default" | "accent" | "success" | "warning";
}) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900">
      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
        {label}
      </p>
      <p
        className={cn("mt-1 text-3xl font-bold tabular-nums", {
          "text-neutral-900 dark:text-neutral-100": variant === "default",
          "text-blue-600 dark:text-blue-400": variant === "accent",
          "text-green-600 dark:text-green-400": variant === "success",
          "text-amber-600 dark:text-amber-400": variant === "warning",
        })}
      >
        {value}
      </p>
    </div>
  );
}

// ============ Signal Indicator ============
function SignalIndicator({ strength }: { strength: string }) {
  const normalized = strength.toLowerCase();
  return (
    <div className="flex items-center gap-2">
      <span
        className={cn("size-2 rounded-full", {
          "bg-green-500 shadow-[0_0_8px_theme(colors.green.500)]":
            normalized === "very high",
          "bg-lime-500": normalized === "high",
          "bg-amber-500": normalized === "medium-high",
          "bg-neutral-500": normalized === "medium",
        })}
      />
      <span className="text-sm text-neutral-600 dark:text-neutral-400">{strength}</span>
    </div>
  );
}

// ============ Loading Skeleton ============
function LoadingSkeleton() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="size-6 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-500 dark:border-neutral-700" />
      <span className="ml-3 text-neutral-600 dark:text-neutral-400">Loading...</span>
    </div>
  );
}

// ============ Empty State ============
function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="py-16 text-center">
      <h3 className="text-lg font-medium text-neutral-900 text-balance dark:text-neutral-100">
        {title}
      </h3>
      <p className="mt-1 text-sm text-neutral-500 text-pretty">{description}</p>
    </div>
  );
}

// ============ Companies View ============
function CompaniesView({
  onSelectCompany,
}: {
  onSelectCompany: (id: Id<"companies">) => void;
}) {
  const [filterIcp, setFilterIcp] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  const stats = useQuery(api.companies.getStats);
  const companies = useQuery(api.companies.list);

  if (!stats || !companies) {
    return <LoadingSkeleton />;
  }

  let filtered = companies;
  if (filterIcp !== "all") {
    filtered = filtered.filter((c) => c.icp === filterIcp);
  }
  if (filterStatus !== "all") {
    filtered = filtered.filter((c) => c.status === filterStatus);
  }
  if (filterPriority !== "all") {
    filtered = filtered.filter((c) => c.priority === filterPriority);
  }
  if (searchTerm) {
    const term = searchTerm.toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.whyFit.toLowerCase().includes(term)
    );
  }

  const icpOptions = Object.keys(stats.byIcp);
  const statusOptions = Object.keys(stats.byStatus);
  const priorityOptions = Object.keys(stats.byPriority);

  return (
    <>
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="Total Companies"
          value={stats.totalCompanies}
          variant="accent"
        />
        <StatCard
          label="Total Contacts"
          value={stats.totalContacts}
          variant="success"
        />
        <StatCard
          label="Highest Priority"
          value={stats.byPriority["Highest"] || 0}
          variant="warning"
        />
        <StatCard
          label="In Research"
          value={stats.byStatus["Researching"] || 0}
        />
      </div>

      {/* Filters */}
      <div className="mt-6 flex flex-wrap gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">Search</label>
          <Input
            type="text"
            placeholder="Search companies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-48"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">ICP</label>
          <Select value={filterIcp} onValueChange={setFilterIcp}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All ICPs" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All ICPs</SelectItem>
              {icpOptions.map((icp) => (
                <SelectItem key={icp} value={icp}>
                  {icp}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">
            Priority
          </label>
          <Select value={filterPriority} onValueChange={setFilterPriority}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              {priorityOptions.map((p) => (
                <SelectItem key={p} value={p}>
                  {p}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">Status</label>
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              {statusOptions.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6 overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Company
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Domain
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Priority
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Signal
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Why Fit
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Status
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7}>
                  <EmptyState
                    title="No companies found"
                    description="Try adjusting your filters"
                  />
                </td>
              </tr>
            ) : (
              filtered.map((company) => (
                <tr
                  key={company._id}
                  className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <td className="px-4 py-3">
                    {company.domain ? (
                      <a
                        href={`https://${company.domain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:text-blue-700 hover:underline dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        {company.name}
                      </a>
                    ) : (
                      <p className="font-medium text-neutral-900 dark:text-neutral-100">{company.name}</p>
                    )}
                    <p className="mt-0.5 text-xs text-neutral-500">
                      {company.icp}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    {company.domain ? (
                      <a
                        href={`https://${company.domain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-neutral-600 hover:text-blue-600 hover:underline dark:text-neutral-400 dark:hover:text-blue-400"
                      >
                        {company.domain}
                      </a>
                    ) : (
                      <span className="text-sm text-neutral-400 dark:text-neutral-600">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={getBadgeVariant(company.priority)}>
                      {company.priority}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <SignalIndicator strength={company.signalStrength} />
                  </td>
                  <td className="max-w-xs px-4 py-3">
                    <p className="truncate text-sm text-neutral-600 dark:text-neutral-400">
                      {company.whyFit}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={getBadgeVariant(company.status)}>
                      {company.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => onSelectCompany(company._id)}
                    >
                      View
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ============ Company Modal ============
function CompanyModal({
  companyId,
  onClose,
}: {
  companyId: Id<"companies"> | null;
  onClose: () => void;
}) {
  const data = useQuery(
    api.companies.getWithContacts,
    companyId ? { companyId } : "skip"
  );
  const updateStatus = useMutation(api.companies.updateStatus);

  if (!companyId) return null;

  const handleStatusChange = async (newStatus: string) => {
    await updateStatus({ id: companyId, status: newStatus });
  };

  return (
    <Dialog open={!!companyId} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        {!data ? (
          <div className="p-6">
            <LoadingSkeleton />
          </div>
        ) : !data.company ? null : (
          <>
            <DialogHeader>
              <DialogTitle>{data.company.name}</DialogTitle>
              <DialogClose asChild>
                <button
                  className="text-2xl text-neutral-400 hover:text-neutral-100"
                  aria-label="Close dialog"
                >
                  ×
                </button>
              </DialogClose>
            </DialogHeader>
            <DialogBody className="space-y-6">
              {/* Details */}
              <section>
                <h3 className="mb-3 text-sm font-semibold text-neutral-600 dark:text-neutral-400">
                  Details
                </h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-neutral-500">ICP</dt>
                    <dd className="text-neutral-900 dark:text-neutral-100">{data.company.icp}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-neutral-500">Priority</dt>
                    <dd>
                      <Badge variant={getBadgeVariant(data.company.priority)}>
                        {data.company.priority}
                      </Badge>
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-neutral-500">Signal</dt>
                    <dd>
                      <SignalIndicator strength={data.company.signalStrength} />
                    </dd>
                  </div>
                  <div>
                    <dt className="text-neutral-500">Why Fit</dt>
                    <dd className="mt-1 text-neutral-900 text-pretty dark:text-neutral-100">
                      {data.company.whyFit}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-neutral-500">Decision Makers</dt>
                    <dd className="mt-1 text-neutral-900 dark:text-neutral-100">
                      {data.company.decisionMakerTitles}
                    </dd>
                  </div>
                </dl>
              </section>

              {/* Status */}
              <section>
                <h3 className="mb-3 text-sm font-semibold text-neutral-600 dark:text-neutral-400">
                  Status
                </h3>
                <Select
                  value={data.company.status}
                  onValueChange={handleStatusChange}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="New">New</SelectItem>
                    <SelectItem value="Researching">Researching</SelectItem>
                    <SelectItem value="Contacted">Contacted</SelectItem>
                    <SelectItem value="Meeting Scheduled">
                      Meeting Scheduled
                    </SelectItem>
                    <SelectItem value="Proposal">Proposal</SelectItem>
                    <SelectItem value="Closed Won">Closed Won</SelectItem>
                    <SelectItem value="Closed Lost">Closed Lost</SelectItem>
                  </SelectContent>
                </Select>
              </section>

              {/* Contacts */}
              <section>
                <h3 className="mb-3 text-sm font-semibold text-neutral-600 dark:text-neutral-400">
                  Contacts ({data.contacts.length})
                </h3>
                {data.contacts.length === 0 ? (
                  <p className="text-sm text-neutral-500">No contacts found</p>
                ) : (
                  <div className="space-y-2">
                    {data.contacts
                      .sort((a, b) => b.personaScore - a.personaScore)
                      .slice(0, 5)
                      .map((contact) => (
                        <div
                          key={contact._id}
                          className="rounded-lg bg-neutral-100 p-3 dark:bg-neutral-800"
                        >
                          <p className="font-medium text-neutral-900 dark:text-neutral-100">
                            {contact.name}
                          </p>
                          <p className="mt-0.5 text-sm text-neutral-600 dark:text-neutral-400">
                            {contact.title}
                          </p>
                          <div className="mt-2 flex items-center gap-3 text-xs text-neutral-500">
                            <span>{contact.jobLevel}</span>
                            <span className="tabular-nums">
                              Score: {contact.personaScore}
                            </span>
                            {contact.linkedinUrl && (
                              <a
                                href={contact.linkedinUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline dark:text-blue-400"
                              >
                                LinkedIn
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    {data.contacts.length > 5 && (
                      <p className="text-sm text-neutral-500">
                        + {data.contacts.length - 5} more contacts
                      </p>
                    )}
                  </div>
                )}
              </section>

              {/* Signals */}
              {data.signals.length > 0 && (
                <section>
                  <h3 className="mb-3 text-sm font-semibold text-neutral-600 dark:text-neutral-400">
                    Signals ({data.signals.length})
                  </h3>
                  <div className="space-y-2">
                    {data.signals.map((signal) => (
                      <div
                        key={signal._id}
                        className="rounded-lg bg-neutral-100 p-3 dark:bg-neutral-800"
                      >
                        <p className="font-medium text-neutral-900 dark:text-neutral-100">
                          {signal.title}
                        </p>
                        <p className="mt-0.5 text-sm text-neutral-600 text-pretty dark:text-neutral-400">
                          {signal.description}
                        </p>
                        <div className="mt-2 flex items-center gap-3 text-xs text-neutral-500">
                          <span>{signal.signalType}</span>
                          {signal.sourceUrl && (
                            <a
                              href={signal.sourceUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline dark:text-blue-400"
                            >
                              Source
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </DialogBody>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

// ============ Contacts View ============
function ContactsView() {
  const [filterJobLevel, setFilterJobLevel] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const contacts = useQuery(api.contacts.list);

  if (!contacts) {
    return <LoadingSkeleton />;
  }

  let filtered = contacts;
  if (filterJobLevel !== "all") {
    filtered = filtered.filter((c) => c.jobLevel === filterJobLevel);
  }
  if (searchTerm) {
    const term = searchTerm.toLowerCase();
    filtered = filtered.filter(
      (c) =>
        c.name.toLowerCase().includes(term) ||
        c.title.toLowerCase().includes(term) ||
        c.companyName.toLowerCase().includes(term)
    );
  }

  const jobLevels = [...new Set(contacts.map((c) => c.jobLevel))];

  return (
    <>
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="Total Contacts"
          value={contacts.length}
          variant="accent"
        />
        <StatCard
          label="Decision Makers"
          value={contacts.filter((c) => c.roleType === "Decision Maker").length}
          variant="success"
        />
        <StatCard
          label="VPs"
          value={contacts.filter((c) => c.jobLevel === "VP").length}
          variant="warning"
        />
        <StatCard
          label="Directors"
          value={contacts.filter((c) => c.jobLevel === "Director").length}
        />
      </div>

      {/* Filters */}
      <div className="mt-6 flex flex-wrap gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">Search</label>
          <Input
            type="text"
            placeholder="Search contacts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-48"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-neutral-500">
            Job Level
          </label>
          <Select value={filterJobLevel} onValueChange={setFilterJobLevel}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="All Levels" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              {jobLevels.map((level) => (
                <SelectItem key={level} value={level}>
                  {level}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Table */}
      <div className="mt-6 overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Name
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Company
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Title
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Level
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Score
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800">
            {filtered.slice(0, 100).map((contact) => (
              <tr
                key={contact._id}
                className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
              >
                <td className="px-4 py-3">
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">{contact.name}</p>
                  {contact.linkedinUrl && (
                    <a
                      href={contact.linkedinUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline dark:text-blue-400"
                    >
                      LinkedIn
                    </a>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-neutral-700 dark:text-neutral-300">
                  {contact.companyName}
                </td>
                <td className="max-w-[200px] px-4 py-3">
                  <p className="truncate text-sm text-neutral-600 dark:text-neutral-400">
                    {contact.title}
                  </p>
                </td>
                <td className="px-4 py-3">
                  <Badge variant={getBadgeVariant(contact.jobLevel)}>
                    {contact.jobLevel}
                  </Badge>
                </td>
                <td className="px-4 py-3 tabular-nums text-neutral-700 dark:text-neutral-300">
                  {contact.personaScore}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={getBadgeVariant(contact.outreachStatus)}>
                    {contact.outreachStatus}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {filtered.length > 100 && (
        <p className="mt-4 text-sm text-neutral-500">
          Showing 100 of {filtered.length} contacts
        </p>
      )}
    </>
  );
}

// ============ Outreach View ============
function OutreachView() {
  const stats = useQuery(api.outreach.getStats);
  const recentOutreach = useQuery(api.outreach.getRecent, { limit: 50 });

  if (!stats || !recentOutreach) {
    return <LoadingSkeleton />;
  }

  return (
    <>
      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Sent" value={stats.totalSent} variant="accent" />
        <StatCard
          label="Replied"
          value={stats.totalReplied}
          variant="success"
        />
        <StatCard
          label="Reply Rate"
          value={`${stats.replyRate.toFixed(1)}%`}
          variant="warning"
        />
        <StatCard
          label="Channels"
          value={Object.keys(stats.byChannel).length}
        />
      </div>

      {/* By Channel */}
      {Object.keys(stats.byChannel).length > 0 && (
        <div className="mt-6">
          <h3 className="mb-3 text-sm font-semibold text-neutral-600 dark:text-neutral-400">
            By Channel
          </h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(stats.byChannel).map(([channel, count]) => (
              <div
                key={channel}
                className="rounded-lg border border-neutral-200 bg-white px-4 py-3 dark:border-neutral-800 dark:bg-neutral-900"
              >
                <p className="text-xs capitalize text-neutral-500">{channel}</p>
                <p className="mt-1 text-xl font-bold tabular-nums text-neutral-900 dark:text-neutral-100">
                  {count as number}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="mt-6 overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800">
        <table className="w-full">
          <thead>
            <tr className="border-b border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900">
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Date
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Channel
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Type
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                Response
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800">
            {recentOutreach.length === 0 ? (
              <tr>
                <td colSpan={4}>
                  <EmptyState
                    title="No outreach yet"
                    description="Start reaching out to contacts to see activity here"
                  />
                </td>
              </tr>
            ) : (
              recentOutreach.map((o) => (
                <tr
                  key={o._id}
                  className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                >
                  <td className="px-4 py-3 tabular-nums text-sm text-neutral-700 dark:text-neutral-300">
                    {new Date(o.sentAt).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-sm capitalize text-neutral-700 dark:text-neutral-300">
                    {o.channel}
                  </td>
                  <td className="px-4 py-3 text-sm text-neutral-600 dark:text-neutral-400">
                    {o.messageType}
                  </td>
                  <td className="px-4 py-3">
                    {o.response ? (
                      <Badge
                        variant={
                          o.response === "replied" ||
                          o.response === "meeting_booked"
                            ? "success"
                            : "default"
                        }
                      >
                        {o.response}
                      </Badge>
                    ) : (
                      <span className="text-sm text-neutral-500">
                        Awaiting response
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
