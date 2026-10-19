# Graph interaction and Overview corrections

The user's screenshot showed equal-size nodes and overlapping labels. Source inspection identified fixed-frame clamping and automatic focus recentering as contributing causes.

Pointer dragging now moves the selected node independently of canvas pan/zoom. Pointer focus does not reveal/recenter nodes. Keyboard reveal occurs only for an offscreen node and preserves zoom. Pointer-up/cancel clears the drag state; dragging suppresses inspection clicks. Empty searches correctly detach and reattach zoom controls when results return.

Circle diameters communicate type: file 54px, class 46px, endpoint 44px, intent 38px, rule 36px, function/call 28px, test 22px. A gently anchored D3 layout accounts for node/label boxes, separates remaining rectangle overlaps and expands its bounds instead of clamping outlying nodes together. Search and Fit work with the visible node set.

Overview shows original contract operations and original source calls before change results. Expand an operation for requests, responses and complete operation/path settings. Changes expose both retained sides, including required flags, security, shared settings and metadata. Unchanged contracts still show the original details. Historical runs are enriched read-only from hash-checked retained snapshots; original results are not rewritten.

Current SIG construction uses static source analysis, literal route relationships, source docstrings and developer declarations. It makes no AI request. AI repair generation remains a separate explicit action.

Verification: 47 frontend tests passed, production build passed, lint has six pre-existing demo warnings. A dense 48-node layout test found no overlap between estimated node/label boxes; pointer and keyboard camera behavior have regression tests. 31 targeted backend tests passed, followed by 12 API/overview checks after the final metadata guard. Independent source review identified and cleared the empty-search lifecycle and incomplete before/after display issues. The running banking report exposes six original operations, four operation changes and V1/V2 metadata. Fresh browser interaction/visual verification remains pending because browser capture was denied; mathematical/source checks are not a browser drag test.
