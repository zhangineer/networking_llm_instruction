examples = """
* how to get a list of Tenants?
moquery -c fvTenant
* how to get a list of EPGs?
moquery -c fvAEPg
* how to get a list of path bindings?
moquery -c fvRsPathAtt
* how to get a list of filters?
moquery -c vzFilter
* how to find a list of VPC paired devices?
moquery -c fabricExplicitGEp
* how to get the fabric-wide settings?
moquery -c infraSetPol
* how to get a list of LLDP neighbor mapping?
moquery -c lldpAdjEp
* how to get a list of vpc policy groups?
moquery -c infraAccBndlGrp
* how to get a list of interface link speed policies?
moquery -c fabricHIfPol
* how to find the current fabric healthscore?
moquery -d topology/HDfabricOverallHealth5min-0
* how to check if EPG VLAN validation is not enforced?
moquery -c infraSetPol -x 'query-target-filter=eq(infraSetPol.validateOverlappingVlans,"no")'
* how to check if the fabric EP dampening is no disabled?
moquery -c infraSetPol -x 'query-target-filter=eq(infraSetPol.disableEpDampening,"no")'
* how to get a list of BDs in tenant demo?
moquery -c fvBD -x 'query-target-filter=wcard(fvBD.dn,"/tn-demo/")'
* how to get all BDs with unicast routing enabled in Tenant demo?
moquery -c fvBD -x 'query-target-filter=and(wcard(fvBD.dn,"/tn-demo/"),eq(fvBD.unicastRoute,"yes"))'
* how to find the fabric TEP address pool?
moquery -c topSystem -x 'query-target-filter=eq(topSystem.role,"controller")'
* how to get a list of device serial numbers and models, excluding the controllers?
moquery -c fabricNode -x 'query-target-filter=ne(fabricNode.role,"controller")'
* how to find a list of interfaces that are admin down?
moquery -c l1PhysIf -x 'query-target-filter=eq(l1PhysIf.adminSt,"down")'
* how to get a list of subnets advertised out and also route leaked?
moquery -c fvSubnet -x 'query-target-filter=eq(fvSubnet.scope,"public,shared")'
* how to find the subnet configured with "192.168.5.1/24"?
moquery -c fvSubnet -x 'query-target-filter=eq(fvSubnet.ip,"192.168.5.1/24")'
* how to get all BDs that has a subnet configured?
moquery -c fvBD -x rsp-subtree-class=fvSubnet rsp-subtree=children rsp-subtree-include=required
* how to get a list of BDs excluding the default ones?
moquery -c fvBD -x 'query-target-filter=and(ne(fvBD.name,"inb"),ne(fvBD.name,"ave-ctrl"),ne(fvBD.name,"default"))'
* how to get all BDs with unicast routing disabled in Tenant demo?
moquery -c fvBD -x 'query-target-filter=and(wcard(fvBD.dn,"uni/tn-demo/"),eq(fvBD.unicastRoute,"no"))'
* how to get a list of BDs with learning not set to limited subnet only?
moquery -c fvBD -x 'query-target-filter=eq(fvBD.limitIpLearnToSubnets,"no")'
* how to get a list of BDs with non default MAC addresses?
moquery -c fvBD -x 'query-target-filter=ne(fvBD.mac,"00:22:BD:F8:19:FF")'
* how to get a list of BDs with ARP flooding disabled, excluding default BDs?
moquery -c fvBD -x 'query-target-filter=and(eq(fvBD.arpFlood,"no"),ne(fvBD.name,"inb"),ne(fvBD.name,"ave-ctrl"),ne(fvBD.name,"default"))'
* how to get al ist of BDs with descriptions contains the keyword vlan ?
moquery -c fvBD -x 'query-target-filter=wcard(fvBD.descr,"vlan")'
* how to get all VRFs with dataplane learning enabled, excluding the default ones?
moquery -c fvCtx -x 'query-target-filter=and(eq(fvCtx.ipDataPlaneLearning,"enabled"),ne(fvCtx.name,"overlay-1"),ne(fvCtx.name,"default"),ne(fvCtx.name,"copy"),ne(fvCtx.name,"oob"),ne(fvCtx.name,"inb"),ne(fvCtx.name,"ave-ctrl"))'
* how to find a list of devices pending for registration that are also leaf switches?
moquery -c dhcpClient -x 'query-target-filter=and(eq(dhcpClient.clientEvent,"pending"),eq(dhcpClient.configNodeRole,"leaf"))'
* how to get a list of EPGs with preferred group member enabled?
moquery -c fvAEPg -x 'query-target-filter=eq(fvAEPg.prefGrMemb,"include")'
* how to get a list of EPGs with flood encap enabled?
moquery -c fvAEPg -x 'query-target-filter=eq(fvAEPg.floodOnEncap,"enabled")'
* how to get a list of path bindings in VLAN 5?
moquery -c fvRsPathAtt -x 'query-target-filter=eq(fvRsPathAtt.encap,"vlan-5")'
* how to get a list of static path bindings tagged with VLAN 100?
moquery -c fvRsPathAtt -x 'query-target-filter=and(eq(fvRsPathAtt.encap,"vlan-100"),eq(fvRsPathAtt.mode,"regular"))'
* how to get a list of path bindings between vlan 100 and 200?
moquery -c fvRsPathAtt -x 'query-target-filter=bw(fvRsPathAtt.encap,"vlan-100","vlan-200")'
* how to get a list of static path bindings with mode 802.1P ?
moquery -c fvRsPathAtt -x 'query-target-filter=eq(fvRsPathAtt.mode,"native")'
* how to get a list of path bindings in EPG epg_vlan0005 in tenant demo?
moquery -c fvRsPathAtt -x 'query-target-filter=and(wcard(fvRsPathAtt.dn,"epg-epg_vlan0005/"),wcard(fvRsPathAtt.dn,"tn-demo/"))'
* how to get a list of path bindings with immediacy set to on demand?
moquery -c fvRsPathAtt -x 'query-target-filter=eq(fvRsPathAtt.instrImedcy,"lazy")'
* how to get a list of contracts, excluding "default"?
moquery -c vzBrCP -x 'query-target-filter=ne(vzBrCP.name,"default")'
* how to get a list of contracts and related subject filters, exclude any contracts named "default"?
moquery -c vzBrCP -x rsp-subtree=full 'query-target-filter=ne(vzBrCP.name,"default")' rsp-subtree-class=vzRsSubjFiltAtt rsp-subtree-include=required
* how to get a list of filters with permit actions?
moquery -c vzRsSubjFiltAtt -x 'query-target-filter=eq(vzRsSubjFiltAtt.action,"permit")'
* how to get a list of filters, excluding "default"?
moquery -c vzFilter -x 'query-target-filter=ne(vzFilter.name,"default")'
* how to find how many critical faults there are in the fabric?
moquery -c faultInst -x rsp-subtree-include=count 'query-target-filter=eq(faultInst.severity,"critical")'
* how to get a list of configration related faults in Tenant demo, ordered by severity with critical being at the top?
moquery -c faultInst -x 'query-target-filter=and(eq(faultInst.type,"config"),wcard(faultInst.dn,"tn-demo/"))' 'order-by=faultInst.severity|desc'
* how to find the total number of configuration changes created between 2024-03-20 and 2024-03-25?
moquery -c aaaModLR -x 'query-target-filter=and(eq(aaaModLR.ind,"creation"),bw(aaaModLR.created,"2024-03-20T00:00","2024-03-25T23:59"))' rsp-subtree-include=count
* how to find all changes made to bridge domain bd_infra since 2024-03-20?
moquery -c aaaModLR -x 'query-target-filter=and(wcard(aaaModLR.affected,"BD-bd_infra/"),ge(aaaModLR.created,"2024-03-20"))'
* how to find all changes made to bridge domain bd_app in Tenant demo since 2024-03-20?
moquery -c aaaModLR -x 'query-target-filter=and(wcard(aaaModLR.affected,"tn-demo/BD-bd_app/"),ge(aaaModLR.created,"2024-03-20"))'
* how to get a list of devices that were rebooted on or after 2024-01-23?
moquery -c topSystem -x 'query-target-filter=ge(topSystem.lastRebootTime,"2024-01-23")'
* how to get a list of devices not running version simsw-6.0(2h)?
moquery -c fabricNode -x 'query-target-filter=ne(fabricNode.version,"simsw-6.0(2h)")'
* how to get a list of L3out along with the domain associated?
moquery -c l3extOut -x rsp-subtree=children rsp-subtree-include=required rsp-subtree-class=l3extRsL3DomAtt
* how to get a list of L3out along with the prefixes?
moquery -c l3extOut -x rsp-subtree=full rsp-subtree-include=required rsp-subtree-class=l3extSubnet
* how to get the VPC leaf switch pair configured with a virtual IP of 0.0.0.0?
moquery -c fabricExplicitGEp -x 'query-target-filter=eq(fabricExplicitGEp.virtualIp,"0.0.0.0")'
* how to get a list of critical faults?
moquery -c faultInst -x 'query-target-filter=eq(faultInst.severity,"critical")'
* how to get a list of faults with severity above "major", return only the top 20 results?
moquery -c faultInst -x page-size=20 'query-target-filter=gt(faultInst.severity,"major")'
* how to get all BDs configured with a subnet scope of at least "public"?
moquery -c fvBD -x rsp-subtree-class=fvSubnet rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=wcard(fvSubnet.scope,"public")'
* how to get a list of BDs using "default" vrf?
moquery -c fvBD -x rsp-subtree-class=fvRsCtx rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=eq(fvRsCtx.tnFvCtxName,"default")'
* how to get a list of BDs with faults?
moquery -c fvBD -x rsp-subtree-include=faults,no-scoped query-target=subtree
* how to get a list of access and VPC policy groups that uses the "lldp_enabled" interface policy?
moquery -c infraAccBndlGrp,infraAccPortGrp -x rsp-subtree-class=infraRsLldpIfPol rsp-subtree-include=required rsp-subtree=children 'rsp-subtree-filter=eq(infraRsLldpIfPol.tnLldpIfPolName,"lldp_enabled")'
* how to get a list of interface profiles and port selectors that are using access policy group "phys_bm"?
moquery -c infraAccPortP -x rsp-subtree=full rsp-subtree-class=infraRsAccBaseGrp 'rsp-subtree-filter=wcard(infraRsAccBaseGrp.tDn,"/accportgrp-phys_bm")'
* how to get a list of EPGs associated with "home_dvs" VMM domain?
moquery -c fvAEPg -x rsp-subtree-class=fvRsDomAtt rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=wcard(fvRsDomAtt.tDn,"home_dvs")'
* how to get a list of EPGs that contains a vmm domain deployed with pre-provision setting?
moquery -c fvAEPg -x rsp-subtree-class=fvRsDomAtt rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=and(eq(fvRsDomAtt.tCl,"vmmDomP"),eq(fvRsDomAtt.resImedcy,"pre-provision"))'
* how to get a list of path bindings modified between 2024-03-20 and 2024-03-25 configured by user named admin?
moquery -c aaaModLR -x 'query-target-filter=and(bw(aaaModLR.created,"2024-03-20","2024-03-25"),wcard(aaaModLR.affected,"/rspathAtt"),eq(aaaModLR.user,"admin"))'
* how to find all the EPGs that contains the physical domain named "netcentric_dom"?
moquery -c fvAEPg -x rsp-subtree-class=fvRsDomAtt rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=wcard(fvRsDomAtt.tDn,"/phys-netcentric_dom")'
* how to get a list of BDs associated with vrf vrf_common?
moquery -c fvBD -x rsp-subtree-class=fvRsCtx rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=eq(fvRsCtx.tnFvCtxName,"vrf_common")'
* how to get a list of BDs associated with vrf vrf_demo in Tenant demo?
moquery -c fvBD -x rsp-subtree-class=fvRsCtx rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=eq(fvRsCtx.tDn,"uni/tn-demo/ctx-vrf_demo")'
* how to find all the BDs associated with l3out demo_l3out?
moquery -c fvBD -x rsp-subtree-class=fvRsBDToOut rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=eq(fvRsBDToOut.tnL3extOutName,"demo_l3out")'
* how to find all the L3Outs configured with 0.0.0.0/0 prefix ?
moquery -c l3extOut -x rsp-subtree=full rsp-subtree-include=required rsp-subtree-class=l3extSubnet 'rsp-subtree-filter=eq(l3extSubnet.ip,"0.0.0.0/0")'
* how to get a list of port selectors using VPC policy group "vpc_int03_bm"?
moquery -c infraHPortS -x rsp-subtree=children rsp-subtree-include=required rsp-subtree-class=infraRsAccBaseGrp 'rsp-subtree-filter=wcard(infraRsAccBaseGrp.tDn,"/accbundle-vpc_int03_bm")'
* how to find all the consumers and providers of contract "dns_contract"?
moquery -c fvAEPg -x rsp-subtree=children rsp-subtree-class=fvRsProv,fvRsCons rsp-subtree-include=required 'rsp-subtree-filter=or(eq(fvRsProv.tnVzBrCPName,"dns_contract"),eq(fvRsCons.tnVzBrCPName,"dns_contract"))'
* how to get a list of EPGs associated with BD bd_app regardless of Tenant?
moquery -c fvAEPg -x rsp-subtree-class=fvRsBd rsp-subtree=children rsp-subtree-include=required 'rsp-subtree-filter=eq(fvRsBd.tnFvBDName,"bd_app")'
* how to get a list VLAN pools uses the encap range of 100 - 200?
moquery -c fvnsVlanInstP -x rsp-subtree=children rsp-subtree-class=fvnsEncapBlk rsp-subtree-include=required 'rsp-subtree-filter=or(bw(fvnsEncapBlk.from,"vlan-1","vlan-200"),bw(fvnsEncapBlk.to,"vlan-1","vlan-200"))'
* how to get a list of contracts with filters that permits traffic?
moquery -c vzBrCP -x rsp-subtree=full rsp-subtree-include=required rsp-subtree-class=vzRsSubjFiltAtt 'rsp-subtree-filter=eq(vzRsSubjFiltAtt.action,"permit")'
* how to get a list of filters for dns (port 53 udp and tcp) traffic?
moquery -c vzFilter -x rsp-subtree-class=vzEntry 'rsp-subtree-filter=and(eq(vzEntry.dFromPort,"53"),eq(vzEntry.dToPort,"53"))' rsp-subtree-include=required rsp-subtree=children
* how to get a list of L3out, physical and VMM domains along with the associated AEPs and VLAN pool?
moquery -c l3extDomP,physDomP,vmmDomP -x rsp-subtree-class=infraRtDomP,infraRsVlanNs rsp-subtree-include=required rsp-subtree=children
"""