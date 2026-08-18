"""Generate diagrams/drawio/k8s-windows-build-poc.drawio — nested virtualization layers."""

from html import escape


def frame(color):
    return (
        f"rounded=1;arcSize=3;whiteSpace=wrap;html=1;fillColor=none;strokeColor={color};"
        f"fontColor={color};strokeWidth=2.5;verticalAlign=top;align=left;fontSize=13;"
        f"fontStyle=1;spacingLeft=16;spacingTop=8;"
    )


HOST, VMLAYER, DOCKER, KIND = "#9E9E9E", "#1E88E5", "#FC6D26", "#4fd1c5"
NODE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#20242e;strokeColor=#9B6BE8;"
    "strokeWidth=2;verticalAlign=middle;align=center;"
)
NODE_K8S = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#1b2430;strokeColor=#4fd1c5;"
    "strokeWidth=2;verticalAlign=middle;align=center;"
)
NODE_WIN = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#2a2028;strokeColor=#E57373;"
    "strokeWidth=2.5;verticalAlign=middle;align=center;"
)
EXT = (
    "rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=7 5;fillColor=none;"
    "strokeColor=#9E9E9E;strokeWidth=2;verticalAlign=middle;align=center;"
)
KVMCOL = (
    "rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=7 5;fillColor=none;"
    "strokeColor=#9B6BE8;strokeWidth=2;verticalAlign=middle;align=center;"
)
ARROW = "endArrow=classic;html=1;rounded=1;strokeColor=#1E88E5;strokeWidth=2.5;"
ARROW_LBL = (
    "endArrow=classic;html=1;rounded=1;strokeColor=#4fd1c5;strokeWidth=2.5;"
    "fontColor=#4fd1c5;fontSize=11;labelBackgroundColor=#1b1f28;"
)
ARROW_DASH = (
    "endArrow=classic;html=1;rounded=1;dashed=1;dashPattern=7 5;strokeColor=#9E9E9E;"
    "strokeWidth=2;fontColor=#9aa0a8;fontSize=11;labelBackgroundColor=#1b1f28;"
)


def label(title, lines, size=14):
    body = "<br>".join(lines)
    return (
        f"<b style='font-size:{size}px;color:#e8eaed'>{title}</b><br><br>"
        f"<font color='#9aa0a8' style='font-size:11px'>{body}</font>"
    )


def cell(cid, value, style, x, y, w, h):
    v = f' value="{escape(value, quote=True)}"' if value else ""
    return (
        f'        <mxCell id="{cid}"{v} style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f"        </mxCell>\n"
    )


def edge(eid, src, tgt, style, value="", extra=""):
    v = f' value="{escape(value, quote=True)}"' if value else ""
    return (
        f'        <mxCell id="{eid}"{v} style="{style}{extra}" edge="1" parent="1" '
        f'source="{src}" target="{tgt}">\n'
        f'          <mxGeometry relative="1" as="geometry" />\n'
        f"        </mxCell>\n"
    )


o = []
o.append('<mxfile host="Resume" type="device">\n')
o.append(
    '  <diagram name="Windows Build Orchestration PoC" id="k8s-windows-build-poc">\n'
)
o.append(
    '    <mxGraphModel dx="1820" dy="1030" grid="0" gridSize="10" guides="1" tooltips="1" '
    'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1820" '
    'pageHeight="1030" math="0">\n      <root>\n'
)
o.append('        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n\n')

o.append("        <!-- ============ NESTED VIRTUALIZATION LAYERS ============ -->\n")
o.append(
    cell(
        "l1",
        "1 &#183; ESXi HOST &#8212; physical server, VT-x / AMD-V",
        frame(HOST),
        250,
        40,
        1250,
        930,
    )
)
o.append(
    cell(
        "l2",
        "2 &#183; LINUX VM &#8212; Debian, /dev/kvm exposed to the guest",
        frame(VMLAYER),
        285,
        105,
        1180,
        825,
    )
)
o.append(
    cell(
        "l3",
        "3 &#183; GITLAB RUNNER &#8212; Docker executor, privileged kind-manager image",
        frame(DOCKER),
        320,
        175,
        1110,
        720,
    )
)
o.append(
    cell(
        "l4",
        "4 &#183; KIND CLUSTER &#8212; Kubernetes nodes as Docker containers",
        frame(KIND),
        355,
        255,
        1040,
        600,
    )
)

o.append("\n        <!-- ============ KIND NODES ============ -->\n")
o.append(
    cell(
        "cp",
        label(
            "Control-plane node",
            ["kube-apiserver &#183; etcd", "scheduler &#183; controller-manager"],
            12,
        ),
        NODE_K8S,
        395,
        310,
        230,
        80,
    )
)
o.append(
    cell(
        "wk",
        label("Worker node", ["kubelet &#183; kube-proxy", "containerd"], 12),
        NODE_K8S,
        660,
        310,
        230,
        80,
    )
)

o.append("\n        <!-- ============ WORKLOADS ============ -->\n")
o.append(
    cell(
        "tsrv",
        label("Temporal server", ["workflow engine", "ClusterIP service"], 13),
        NODE,
        395,
        430,
        210,
        110,
    )
)
o.append(
    cell(
        "twrk",
        label(
            "Temporal worker",
            ["drives the build passes", "one per target platform"],
            13,
        ),
        NODE,
        635,
        430,
        210,
        110,
    )
)
o.append(
    cell(
        "kv",
        label("KubeVirt", ["virt-operator, virt-controller", "virt-launcher pod"], 13),
        NODE,
        875,
        430,
        210,
        110,
    )
)

o.append("\n        <!-- ============ WINDOWS VM ============ -->\n")
o.append(
    cell(
        "win",
        label(
            "Windows VM &#8212; running on KVM",
            [
                "full Windows guest on a Linux-only cluster",
                "&#183;",
                "native C / Rust compilation, no cross-compilation",
                "VirtIO drivers &#183; vCPU / vRAM / vDisk",
            ],
            15,
        ),
        NODE_WIN,
        480,
        640,
        450,
        175,
    )
)
o.append(
    cell(
        "disk",
        label(
            "Boot disk (PVC)",
            [
                "win.qcow2 &#183; Packer + QEMU",
                "unattended.xml install",
            ],
            13,
        ),
        EXT,
        1120,
        430,
        250,
        110,
    )
)

o.append("\n        <!-- ============ EXTERNAL ============ -->\n")
o.append(
    cell(
        "ci",
        label(
            "GitLab CI",
            [
                "triggers the job",
                "&#183;",
                "whole environment rebuilt",
                "from scratch on every run",
            ],
            14,
        ),
        EXT,
        30,
        420,
        180,
        180,
    )
)
o.append(
    cell(
        "kvm",
        label(
            "/dev/kvm passthrough",
            [
                "VT-x / AMD-V",
                "&#8595; ESXi host",
                "&#8595; Debian VM",
                "&#8595; privileged container",
                "&#8595; kind node",
                "&#8595; virt-launcher",
                "&#8595; Windows VM",
                "&#183;",
                "kernel modules checked to",
                "rule out emulation fallback",
            ],
            13,
        ),
        KVMCOL,
        1550,
        270,
        240,
        380,
    )
)
o.append(
    cell(
        "prod",
        label(
            "Production target",
            [
                "RKE2 on native",
                "Windows and Linux servers",
            ],
            13,
        ),
        EXT,
        1550,
        670,
        240,
        115,
    )
)

o.append("\n        <!-- ============ EDGES ============ -->\n")
o.append(edge("e-ci", "ci", "l3", ARROW, "", "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"))
o.append(
    edge(
        "e-kv",
        "kv",
        "win",
        ARROW_LBL,
        "starts the VM",
        "exitX=0.5;exitY=1;entryX=0.85;entryY=0;",
    )
)
o.append(
    edge(
        "e-twrk",
        "twrk",
        "win",
        ARROW_LBL,
        "build tasks",
        "exitX=0.5;exitY=1;entryX=0.35;entryY=0;",
    )
)
o.append(
    edge(
        "e-disk",
        "disk",
        "win",
        ARROW_LBL,
        "boots from",
        "exitX=0.5;exitY=1;entryX=1;entryY=0.3;",
    )
)
o.append(
    edge(
        "e-prod",
        "win",
        "prod",
        ARROW_DASH,
        "same workloads",
        "exitX=1;exitY=0.75;entryX=0;entryY=0.5;",
    )
)

o.append("      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n")

open("diagrams/drawio/k8s-windows-build-poc.drawio", "w", encoding="utf-8").write(
    "".join(o)
)
print("wrote diagrams/drawio/k8s-windows-build-poc.drawio")
