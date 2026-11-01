import dagre from "@dagrejs/dagre";
import { X } from "lucide-react";
import { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";


function applyAutomaticLayout(nodes, edges) {
  const graph = new dagre.graphlib.Graph();

  graph.setDefaultEdgeLabel(() => ({}));

  graph.setGraph({
    rankdir: "TB",
    nodesep: 90,
    ranksep: 125,
    marginx: 50,
    marginy: 50,
  });

  for (const node of nodes) {
    graph.setNode(node.id, {
      width: node.style?.width ?? 190,
      height: 65,
    });
  }

  for (const edge of edges) {
    graph.setEdge(edge.source, edge.target);
  }

  dagre.layout(graph);

  return nodes.map((node) => {
    const position = graph.node(node.id);

    if (!position) return node;

    const width = node.style?.width ?? 190;

    return {
      ...node,
      position: {
        x: position.x - width / 2,
        y: position.y - 32.5,
      },
    };
  });
}

export default function EvidenceGraph({ result, dnsData }) {
  const [selectedNode, setSelectedNode] = useState(null);

  const { nodes, edges } = useMemo(() => {
    const investigation = result?.investigation ?? {};
    const evidence = Array.isArray(result?.evidence)
      ? result.evidence
      : [];

    if (!investigation.url) {
      return { nodes: [], edges: [] };
    }

    let hostname = "Unknown hostname";

    try {
      hostname = new URL(investigation.url).hostname;
    } catch {
      // Keep fallback
    }

    const nodes = [
      {
        id: "target",
        position: { x: 300, y: 40 },
        data: { label: "TARGET URL" },
        style: {
          background: "#29234f",
          color: "#f4f0ff",
          border: "1px solid #ad91ff",
          borderRadius: 12,
          width: 190,
          padding: 16,
          fontWeight: 800,
        },
      },
      {
        id: "hostname",
        position: { x: 300, y: 190 },
        data: { label: hostname },
        style: {
          background: "#102635",
          color: "#8beaff",
          border: "1px solid #45c9e1",
          borderRadius: 12,
          width: 190,
          padding: 15,
          overflowWrap: "anywhere",
        },
      },
    ];

    const edges = [
      {
        id: "target-hostname",
        source: "target",
        target: "hostname",
        label: "hostname",
        animated: true,
        style: { stroke: "#65e8f4" },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: "#65e8f4",
        },
      },
    ];

    evidence.forEach((item, index) => {
      const side = index % 2 === 0 ? -1 : 1;
      const row = Math.floor(index / 2);

      const id = `evidence-${index}`;

      nodes.push({
        id,
        position: {
          x: 300 + side * 285,
          y: 80 + row * 135,
        },
        data: {
          label: `${
            result?.threat_explanations?.[index]?.title ??
            item.code ??
            "INDICATOR"
          } (+${item.points ?? 0})`,
        },
        style: {
          background: "#30231d",
          color: "#ffd29c",
          border: "1px solid #cc9259",
          borderRadius: 12,
          width: 210,
          padding: 14,
          fontSize: 12,
          overflowWrap: "anywhere",
        },
      });

      edges.push({
        id: `edge-${index}`,
        source: "target",
        target: id,
        label: "risk indicator",
        style: { stroke: "#c79b6a" },
      });
    });

    // DNS observations are separate from heuristic risk indicators.
    const dnsRecords = [
      ...(Array.isArray(dnsData?.ipv4) ? dnsData.ipv4 : []).map(
        (ip) => ({ ip, type: "A" })
      ),
      ...(Array.isArray(dnsData?.ipv6) ? dnsData.ipv6 : []).map(
        (ip) => ({ ip, type: "AAAA" })
      ),
    ];

    const dnsMatchesHostname =
      dnsData?.hostname?.toLowerCase() === hostname.toLowerCase();

    if (dnsMatchesHostname) {
      dnsRecords.forEach((record, index) => {
        const id = `dns-${index}`;

        nodes.push({
          id,
          position: {
            x: 170 + (index % 2) * 260,
            y: 350 + Math.floor(index / 2) * 110,
          },
          data: { label: `${record.type} / ${record.ip}` },
          style: {
            background: "#102c3b",
            color: "#8beaff",
            border: "1px solid #45c9e1",
            borderRadius: 12,
            width: 220,
            padding: 14,
            fontSize: 12,
            overflowWrap: "anywhere",
          },
        });

        edges.push({
          id: `dns-edge-${index}`,
          source: "hostname",
          target: id,
          style: {
            stroke: "#45c9e1",
            strokeWidth: 1.6,
          },
        });
      });
    }

    return {
      nodes: applyAutomaticLayout(nodes, edges),
      edges,
    };
  }, [result, dnsData]);

  if (!nodes.length) return null;

  return (
    <section className="v5-graph-panel">
      <div className="v5-graph-header">
        <span>INTERACTIVE EVIDENCE GRAPH</span>
        <small>OFFLINE INDICATOR MAP</small>
      </div>

      <div className="v5-graph-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={(_, node) => setSelectedNode(node)}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
          minZoom={0.25}
          maxZoom={1.6}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#333c59" gap={24} size={1} />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor="#7568c5"
            maskColor="#050710aa"
          />
        </ReactFlow>
      </div>

      {selectedNode && (
        <div className="v5-node-inspector">
          <div className="v5-node-inspector-header">
            <strong>NODE INTELLIGENCE</strong>
            <button
              type="button"
              onClick={() => setSelectedNode(null)}
              aria-label="Close node inspector"
            >
              <X size={18} />
            </button>
          </div>

          <span>NODE IDENTIFIER</span>
          <p>{selectedNode.id}</p>

          <span>NODE INFORMATION</span>
          <p>{selectedNode.data?.label ?? "No information"}</p>

          {selectedNode.id.startsWith("evidence-") && (() => {
            const index = Number(selectedNode.id.split("-")[1]);
            const evidence = result?.evidence?.[index];
            const explanation = result?.threat_explanations?.[index];

            return (
              <>
                {evidence?.explanation && (
                  <>
                    <span>DETECTED EVIDENCE</span>
                    <p>{evidence.explanation}</p>
                  </>
                )}

                {explanation && (
                  <>
                    <span>THREAT EXPLANATION</span>
                    <p>{explanation.title}</p>
                    <p>{explanation.reason}</p>

                    <span>RECOMMENDED PRECAUTION</span>
                    <p>{explanation.action}</p>
                  </>
                )}
              </>
            );
          })()}

          {selectedNode.id.startsWith("dns-") && (() => {
            const index = Number(selectedNode.id.split("-")[1]);
            const records = [
              ...(Array.isArray(dnsData?.ipv4) ? dnsData.ipv4 : [])
                .map((ip) => ({ ip, type: "A / IPv4" })),
              ...(Array.isArray(dnsData?.ipv6) ? dnsData.ipv6 : [])
                .map((ip) => ({ ip, type: "AAAA / IPv6" })),
            ];
            const record = records[index];

            if (!record) return null;

            return (
              <>
                <span>IP ADDRESS</span>
                <p>{record.ip}</p>

                <span>DNS RECORD TYPE</span>
                <p>{record.type}</p>

                <span>SOURCE HOSTNAME</span>
                <p>{dnsData?.hostname ?? "Unknown"}</p>

                <span>DNS RESOLUTION STATUS</span>
                <p>{dnsData?.status ?? "Unknown"}</p>

                <span>ADDRESS CLASSIFICATION</span>
                <p>
                  Publicly routable address returned by DNS lookup.
                  This does not indicate whether the website is safe.
                </p>
              </>
            );
          })()}

          <span>DATA SOURCE</span>
          <p>
            {selectedNode.id.startsWith("dns-")
              ? "DNS lookup result"
              : selectedNode.id.startsWith("evidence-")
                ? "Offline heuristic indicator"
                : "Investigated URL"}
          </p>
        </div>
      )}

      <p className="v5-graph-note">
        Purple nodes represent the investigated URL, amber nodes
        represent heuristic risk indicators, and cyan nodes
        represent DNS lookup results. This graph does not show
        observed redirects or network traffic.
      </p>
    </section>
  );
}
