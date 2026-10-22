import { defineConfig, godoc, markdown } from "sourcey";

// Sourcey build for github.com/gin-gonic/gin at a pinned commit.
// The Go API tab is rendered from godoc.json, a snapshot produced by
// `sourcey godoc` against the pinned clone (see reproduce.md).
export default defineConfig({
  name: "Gin",
  siteUrl: "https://asporeteam.github.io",
  baseUrl: "/gin-sourcey-docs/",
  prettyUrls: "slash",
  repo: "https://github.com/ASporeTeam/gin-sourcey-docs",
  editBranch: "main",
  theme: { name: "api-first" },
  navbar: {
    links: [
      { type: "github", href: "https://github.com/gin-gonic/gin", label: "gin-gonic/gin" },
      { type: "github", href: "https://github.com/ASporeTeam/gin-sourcey-docs", label: "This build" },
    ],
    primary: { type: "button", label: "Go API reference", href: "/gin-sourcey-docs/go/" },
  },
  footer: {
    links: [
      { type: "github", href: "https://github.com/gin-gonic/gin/blob/0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646/LICENSE", label: "gin is MIT licensed" },
      { type: "link", href: "https://sourcey.com", label: "Generated with Sourcey" },
    ],
  },
  navigation: {
    tabs: [
      {
        tab: "Guides",
        slug: "",
        source: markdown({
          groups: [
            {
              group: "Start here",
              pages: ["introduction", "coverage", "gaps", "reproduce"],
            },
          ],
        }),
      },
      {
        tab: "Go API",
        slug: "go",
        source: godoc({
          module: "./gin-src",
          packages: ["./..."],
          mode: "snapshot",
          snapshot: "./godoc.json",
          includeTests: true,
          sourceBasePath: "",
        }),
      },
    ],
  },
});
