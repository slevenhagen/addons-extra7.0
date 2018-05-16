<html>
<head>
    <style type="text/css">
        ${css}
        .main_table{
               margin-top: 0px;
               margin-bottom: 0px;
               font-size:15px;
               text-align:left;
               border:1px black;
               bottom-border:None;
        }
        .table1{
               margin-top: 0px;
               margin-bottom: 0px;
               font-size:13px;
               background-color:black;
               color:white;
               text-align:center;
               border:1px solid gray;
        }
       .table4{
               margin-top: 0px;
               margin-bottom: 0px;
               font-size:13px;
               background-color:gray;
               text-align:center;
               border:1px solid black;
               border-collapse: collapse;
        }
        .table4 td{
        	border:1px solid black;
        }
        .table5{
               margin-top: 0px;
               margin-bottom: 0px;
               font-size:10px;
               text-align:center;
               border:1px solid black;
               border-collapse: collapse;
        }
        .table5 td{
        	border:1px solid gray;
        }
        .table7{
               margin-top: 0px;
               margin-bottom: 0px;
               font-size:7px;
               text-align:left;
               border:1px solid black;
               border-collapse: collapse;
        }
        input[type="checkbox"] {
                           height: 1.2em;
                           width: 1.2em;
                           vertical-align: middle;
                           margin: 0 0.4em 0.4em 0;
                           border: 1px solid rgba(0, 0, 0, 0.3);
                           background: -webkit-linear-gradient(#FCFCFC, #DADADA);
                           -webkit-appearance: none;
                           -webkit-transition: box-shadow 200ms;
                            box-shadow:inset 1px 1px 0 #fff, 0 1px 1px rgba(0,0,0,0.1);
                       }

                       /* checkbox checked */
                       input[type="checkbox"]:checked:before {
                       font-weight: bold;
                       color: rgba(0, 0, 0, 0.7);
                       content: '\2713';
                       -webkit-margin-start: 0;
                       margin-left: 2px;
                       font-size: 0.9em;
                       }
    </style>
</head>
<body>
	<% new_ob = [objects[0]] %>
	%for o in new_ob:
		<% o = objects[0] %>
		<table class="main_table"  width="100%">
			<tr>
				<td width="35%">
				<%
					date = str(o.promise_date)
				%>
					<b> ${'Date'} ${ date.split(' ')[0] or ''|entity} </b>
				</td>
				<td width="40%" font-size:40px;>
					<b> ${'Master Bill of Lading'}</b>
				</td>
				<td width="25%">
					<b> ${'B/L NO'} ${''}</b>
				</td>
			</tr>
			<tr>
			<td style="color:white;">
			</td>
		</tr>
		</table>
		<table class="table1"  width="100%">
		<tr>
			<td>
				${"SHIPPER(ORIGIN)"}
			</td>
			<td>
				${"CONSIGNEE(DESTINATION)"}
			</td>
		</tr>
		</table>
		<table style="display: inline-block; border: 1px solid; float: left; font-size:12px;" width="49.7%" height="60px">
		<tr>
			<td style="font-size=5px;" >
				${"Shipper No."}
			</td>
		</tr>
		<tr>
			<td>
				${"Trailer No."}
			</td>
		</tr>
		<tr>
			<td>
				${"Seal No." }<br/><br/>
			</td>
		</tr>
		</table>
		<table style="display: inline-block; border: 1px solid; float: right; font-size:12px" width="49.9%" height="60px">
		<tr>
			<td>
				${"Name:"}
				%if o.partner_id:
					${o.partner_id.name or ''}
				%endif
			</td>
		</tr>
		<tr>
			<td>
				${"Address: "}
				%if o.partner_id and o.partner_id.street:
                	${o.partner_id and o.partner_id.street or ''|entity},
                %endif
                %if o.partner_id and o.partner_id.street2:
                	${o.partner_id and o.partner_id.street2 or ''|entity},
                %endif
                %if o.partner_id and o.partner_id.city:
                	${o.partner_id and o.partner_id.city or '' |entity},
                %endif
                %if o.partner_id and o.partner_id.state_id:
	                ${o.partner_id and o.partner_id.state_id and o.partner_id.state_id.name or '' |entity},
	            %endif
	            %if o.partner_id and o.partner_id.zip:
                	${o.partner_id and o.partner_id.zip or '' |entity},
                %endif
	            %if o.partner_id and o.partner_id.country_id:
	                ${o.partner_id and o.partner_id.country_id and o.partner_id.country_id.name | entity}
	            %endif
			</td>
		</tr>
		<tr>
			<td style="color:white;">
			</td>
		</tr>

		</table>
		<table style="display: inline-block; border: 1px solid; float:right; font-size:12px; " width="49.9%" height="60px">
		<tr>
			<td>
				${"P.O NO. :"} ${''}<br/>
				<% sales = '' %>
                <% for o in objects:
                    if o.sale_id:
                        sales +=  str(o.sale_id.name) + ', '
                %>
				${"S.O NO. :"} ${sales[:-1]}
			</td>
		</tr>
		<tr>
			<td>
				<br/>
			</td>
		</tr>
		</tr>
			<td>
				<br/>
			</td>
		</tr>
		</table>
		<table style="display: inline-block; border: 1px solid; float: right; font-size:12px;" width="49.7%" height="60px">
		<tr>
			<td>
			    % if o.sale_id and o.sale_id.company_id:
				    ${"Name :"} ${ o.sale_id.company_id.name or '' | entity}
				%else:
				    ${"Name :"} <br/><br/>
				%endif
			</td>
		</tr>
		<tr>
			<td>
			    ${"Address : "}
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.street:
                    ${ o.sale_id.company_id.street or  ''},
                 %endif
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.street2:
                    ${ o.sale_id.company_id.street2 or  ''},
                 %endif
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.city:
                    ${ o.sale_id.company_id.city or ''},
                 %endif
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.state_id:
                    ${ o.sale_id.company_id.state_id.name or ''},
                 %endif
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.zip:
                    ${ o.sale_id.company_id.zip or ''},
                 %endif
                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.country_id:
                    ${o.sale_id.company_id.country_id.name  or ''}
                 %endif
			</td>
		</tr>
		</table>
		<table style="display: inline-block; background-color:black; border: 1px solid black; color:white; float: left;text-align:center; font-size:13px; " width="49.7%" height="24px">
		<tr>
			<td>
				${"THIRD PARTY FREIGHT CHARGES BILL TO"}<br/>
			</td>
		</tr>
		</table>
		<table style="display: inline-block; border: 1px solid; float: right; font-size:12px; border-bottom: None;" width="49.9%" height="86px">
		<tr>
			<td style="font-size:small;">
				<b>${"SPECIAL INSTRUCTION :"}</b>
				<input type="checkbox" style= "text-align:right" name="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}" value="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}" id="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                />${'Master Bill of Lading'}
			</td>
		</tr>
		<tr>
			<td>
				${"Delivery before Noon"} <br/>
			</td>
		</tr>
			<td>
				<br/>
			</td>
		</tr>
		</table>
		<table style="display: inline-block; border: 1px solid; float: left; border-bottom: None; border-left: 1px solid black; font-size:12px;" width="49.7%" height="60px" >
		<tr>
			<td>
				${"Name :"}
					%if o.sale_id and o.sale_id.third_party_bill_to_id:
						${o.sale_id.third_party_bill_to_id.name or '' | entity}
					%endif
			</td>
		</tr>
		<tr>
			<td>
				${"Address:"}
				%if o.sale_id and o.sale_id.third_party_bill_to_id:
						%if o.sale_id.third_party_bill_to_id.street:
							${o.sale_id.third_party_bill_to_id.street or ''},
						%endif
						%if o.sale_id.third_party_bill_to_id.street2:
							${o.sale_id.third_party_bill_to_id.street2 or ''},
						%endif
						%if o.sale_id.third_party_bill_to_id.city:
							${o.sale_id.third_party_bill_to_id.city or ''},
						%endif
						%if o.sale_id.third_party_bill_to_id.state_id:
							${o.sale_id.third_party_bill_to_id.state_id.name or ''},
						%endif
						%if o.sale_id.third_party_bill_to_id.zip:
							${o.sale_id.third_party_bill_to_id.zip or ''},
						%endif
						%if o.sale_id.third_party_bill_to_id.country_id:
							${o.sale_id.third_party_bill_to_id.country_id.name  or ''}
						%endif
				%endif
			</td>
		</tr>
		</tr>
			<td style=" text-align:left; color:white;">
				<br/>
			</td>
		</tr>

		</table>
		<table class="table4"  width="100%">
			<tr>
				<td width="5%">
					${'HU'}
				</td>
				<td width="8%">
					${'HU Type'}
				</td>
				<td width="8%">
					${'PKGs'}
				</td>
				<td width="8%">
					${'PKG type'}
				</td>
				<td width="5%">
					${'HM'}
				</td>
				<td width="38%">
					${'Description of Articles, Special Marks & Exceptions'}
				</td>
				<td width="8%">
					${'NMFC#'}
				</td>
				<td width="8%">
					${'Class'}
				</td>
				<td width="12%">
					${'Weight Subj. to Correction'}
				</td>
			</tr>
		</table>
		<% total = 0 %>
		<% line_count = 0 %>
		<% move_lines = [] %>
		<% move_lines += [line for ob in objects for line in ob.move_lines] %>
		<% obj_count = len(move_lines) %>
		
		%for line in move_lines:
			<% line_count = line_count + 1 %>
			%if line_count % 5 == 0 and line_count > 0 :
				<table class="table5"  width="100%" height="55.5">
					<tr>
						%if get_type(line):
							<td width="5%">
							    %if line.product_packaging and line.product_packaging.qty:
								 ${int(round(line.product_qty / line.product_packaging.qty))}
								%endif
							</td>
							<td width="8%">
							   %if line and line.product_packaging and line.product_packaging.hu_type_id:
								  ${line.product_packaging.hu_type_id.name or '' |entity}
							   %endif
							</td>
							<td width="8%">
								${line.product_qty or '' |entity}
							</td>
							<td width="8%">
								${line.product_uom.name or '' |entity}
							</td>
							<td width="5%">
							</td>
							<td width="38%">
								[${line.product_id.code or '' |entity}] [${line.product_id.cust_code or '' | entity}] ${line.product_id.name or '' |entity}
							</td>
							<td width="8%">
								${o.nmfc or '' | entity}
							</td>
							<td width="8%">
								${o.p_class or '' | entity}
							</td>
							<td width="12%">
							     ${int(round(net_weight(line))) or 0 | entity}
							     <%  total = total +int(round(net_weight(line)))%>
							</td>
						%endif
						%if not get_type(line):
							<td width="5%">
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="5%">
							</td>
							<td style="text-align:left; " width="38%">
							    ${line}
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="12%">
							</td>
						%endif
					</tr>
				</table>
			%if line_count != obj_count:
		            <table class="table5"  width="100%" height="55px" style="font-size:10px; ">
		                <tr>
		                    <td style="border-bottom:1px solid black; text-align:top" width="35%">
		                        ${'Hazardous Material Emergency Contact:'}
		                    </td>
		                    <td style="text-align:left; border-bottom:1px solid black;" width="15%">
		                        <b><u>${'Freight Term :'}</u></b><br/>
		
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'Prepaid':
		                       checked
		                     %endif
		                     />${'Prepaid'} <br/>
		
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'Receiver':
		                       checked
		                     %endif
		                     />${'Collect'}<br/>
		
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'Third Party'}<br/>
		
		                    </td>
		                    <td style=" text-align:left; border-bottom:1px solid black;" width="50%">
		                        <b><u>${'C.O.D  Amount:'}</u></b><br/>
								&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
		
		                         <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                         %if o.sale_id and o.sale_id.incoterm.name == 'Prepaid':
		                           checked
		                         %endif
		                        />${'Prepaid'} <br/>
		
		                        &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
		                        <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                        %if o.sale_id and o.sale_id.incoterm.name == 'Receiver':
		                            checked
		                        %endif
		                     />${'Collect'}<br/>
		
		                     &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
		                      <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'Customer Check Acceptable'}<br/>
		                    </td>
		                </tr>
		            </table>
		            <table class="table7"  width="100%">
		                <tr>
		                    <td style=" text-align:left; font-size:9px; border:1px solid black;" width="50%" height="5px">
		                        ${'DECLARED VALUE :Where the rate is dependent on value,shippers are required to state specifically in writing the agreed of declared value of the property as follows.'}<br/>
		                        ${'The agreed of declared value of the property is specifically stated by the shipper to be not'} <br/><br/>
		
		                        ${'exceeding____________________________ per ____________________________'} <br/><br/>
		
		                    </td>
		                    <td style=" text-align:left; font-size:9px; border:1px solid black;" width="50%" height="5px">
		                        ${'The carrier shall not make delivery of the shipment without payment of freight and all other lawful \n charges'} <br/>
		                        ${'______________________________________Shipper Signature'}
		
		                    </td>
		                </tr>
		            </table>
		            <table class="table7"  width="100%">
		                <tr>
		                    <td style=" text-align:left; border:1px solid black; font-size:10px;" width="50%">
		                        ${'NOTE Liability Limitation for loss of damage in this shipment may be applicable. See 49 U.S.C - 14706(c)(1)(A) and (B) '}<br/>
		                    </td>
		                </tr>
		            </table>
		            <table class="table7"  width="100%">
		                <tr>
		                    <td style=" text-align:left; border:1px solid black; font-size:10px;" width="50%">
		                        ${'RECEIVED Subject to individually determined rates or contracts that have been agreed upon in writing between the carrier and shipper, if applicable otherwise to the rates'}
		                        ${'classifications and rules that have been established by the carrier and are available to the shipper on request. The property described above, in apparent good order except as noted'}
		                        ${'(contents and condition of packages unknown) marked, consigned and destined as show above, which said carrier agrees to carry to destination, if on its route or otherwise deliver to another carrier'}
		                        ${'on the route to destination. Every service to be performed hereunder shall be subject to all bill of lading terms and conditions in the governing classification on the date of the'}
		                        ${'shipment. Shipper here by certifier that is here by familiar with all the bill of lading terms and conditions in the governing classification and the said terms and conditions are here by '}
		                        ${'agreed to by the shipper and accepted for himself and his assigns'}
		                    </td>
		                </tr>
		                <tr>
		                    <td style=" text-align:left; border:1px solid black; font-size:9px;" width="50%" height="18px">
		                        ${'This is to certify that the above named materials and property classified,described, packaged,marked and labeled. and are in proper condition of transaction according to the applicable'}
		                        ${'regulations of the Department of Transportation '}
		                    </td>
		                </tr>
		            <table class="table7"  width="100%">
		                <tr>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'SHIPPER COMPANY NAME'} <br/>
		                        ${company.name}
		                    </td>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'CARRIER'} <br/>
		                    </td>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'CONSIGNEE'} <br/>
		                    </td>
		                    <td style=" text-align:left; border-bottom:0px solid white; font-size:8px;" width="25%">
		                        <u> ${'TRAILER LOADED'} </u><br/>
		
		                    <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'By Shipper'}<br/>
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'By Driver'}<br/>
		
		                    </td>
		                </tr>
		                <tr>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'SHIPPING SIGNATURE/DATE'} <br/>
		                    </td>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'DRIVER SIGNATURE/DATE'} <br/>
		                    </td>
		                    <td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
		                        ${'CONSIGNEE SIGNATURE/DATE'} <br/>
		                    </td>
		                    <td style=" text-align:left; border-bottom:1px solid black; font-size:8px;" width="25%">
		                        <u> ${'FREIGHT COUNTER'} </u><br/>
		
		                    <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'By Shipper'}<br/>
		
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'By Driver/Pallets said to contain'}<br/>
		
		                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                     />${'By Driver/Pieces'}<br/>
		                    </td>
		                </tr>
		            </table>
						<p style="page-break-after:always"></p>
						<br/><br/>
						<table class="main_table"  width="100%">
		            <tr>
		                <td width="35%">
		                <%
		                    date = str(o.promise_date)
		                %>
		                    <b> ${'Date'} ${ date.split(' ')[0] or ''|entity} </b>
		                </td>
		                <td width="40%" font-size:40px;>
		                    <b> ${'Master Bill of Lading'}</b>
		                </td>
		                <td width="25%">
		                    <b> ${'B/L NO'} ${''}</b>
		                </td>
		            </tr>
		            <tr>
					<td style="color:white;">
					</td>
					</tr>
		        </table>
		        <table class="table1"  width="100%">
		        <tr>
		            <td>
		                ${"SHIPPER(ORIGIN)"}
		            </td>
		            <td>
		                ${"CONSIGNEE(DESTINATION)"}
		            </td>
		        </tr>
		        </table>
		        <table style="display: inline-block; border: 1px solid; float: left; font-size:12px;" width="49.7%" height="60px">
		        <tr>
		            <td style="font-size=5px;" >
		                ${"Shipper No."}
		            </td>
		        </tr>
		        <tr>
		            <td>
		                ${"Trailer No."}
		            </td>
		        </tr>
		        <tr>
		            <td>
		                ${"Seal No." }<br/><br/>
		            </td>
		        </tr>
		        </table>
		
		        <table style="display: inline-block; border: 1px solid; float: right; font-size:12px;" width="49.99%" height="60px">
		
		        <tr>
		            <td>
		                ${"Name:"}
		                %if o.partner_id:
		                    ${o.partner_id.name or ''}
		                %endif
		            </td>
		        </tr>
		        <tr>
		            <td>${"Address: "}
		                %if o.partner_id and o.partner_id.street:
		                    ${o.partner_id and o.partner_id.street or ''|entity},
		                %endif
		                %if o.partner_id and o.partner_id.street2:
		                    ${o.partner_id and o.partner_id.street2 or ''|entity},
		                %endif
		                %if o.partner_id and o.partner_id.city:
		                    ${o.partner_id and o.partner_id.city or '' |entity},
		                %endif
		                %if o.partner_id and o.partner_id.state_id:
		                    ${o.partner_id and o.partner_id.state_id and o.partner_id.state_id.name or '' |entity},
		                %endif
		                %if o.partner_id and o.partner_id.zip:
		                    ${o.partner_id and o.partner_id.zip or '' |entity},
		                %endif
		                %if o.partner_id and o.partner_id.country_id:
		                    ${o.partner_id and o.partner_id.country_id and o.partner_id.country_id.name | entity}
		                %endif
		            </td>
		        </tr>
		        <tr>
		            <td>
		            	<br/>
		            </td>
		        </tr>
		
		        </table>
		        <table style="display: inline-block; border: 1px solid; float:right; font-size:12px; " width="49.9%" height="60px">
		        <tr>
		            <td>
		                ${"P.O NO. :"} ${''}<br/><br/>
		                <% sales = '' %>
		                <% for o in objects:
		                    if o.sale_id:
		                        sales +=  str(o.sale_id.name) + ', '
		                %>
		                ${"S.O NO. :"} ${sales[:-1]}<br/>
		            </td>
		        </tr>
		        <tr>
		            <td>
		                <br/>
		            </td>
		        </tr>
		        </tr>
		            <td>
		                <br/>
		            </td>
		        </tr>
		        </table>
		        <table style="display: inline-block; border: 1px solid; float: right; font-size:12px;" width="49.7%" height="60px">
		        <tr>
		            <td>
		            	% if o.sale_id and o.sale_id.company_id:
				    		${"Name :"} ${ o.sale_id.company_id.name or '' | entity}
						%else:
				    		${"Name :"} <br/><br/>
						%endif
		            </td>
		        </tr>
		        <tr>
		            <td>
		            ${"Address : "}
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.street:
		                    ${ o.sale_id.company_id.street or  ''},
		                 %endif
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.street2:
		                    ${ o.sale_id.company_id.street2 or  ''},
		                 %endif
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.city:
		                    ${ o.sale_id.company_id.city or ''},
		                 %endif
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.state_id:
		                    ${ o.sale_id.company_id.state_id.name or ''},
		                 %endif
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.zip:
		                    ${ o.sale_id.company_id.zip or ''},
		                 %endif
		                 %if o.sale_id and o.sale_id.company_id and o.sale_id.company_id.country_id:
		                    ${o.sale_id.company_id.country_id.name  or ''}
		                 %endif
		            </td>
		        </tr>
		        </table>
		        <table style="display: inline-block; background-color:black; border: 1px solid black; color:white; float: left;text-align:center; font-size:13px; " width="49.7%" height="24px">
		        <tr>
		            <td>
		                ${"THIRD PARTY FREIGHT CHARGES BILL TO"}<br/>
		            </td>
		        </tr>
		        </table>
		        <table style="display: inline-block; border: 1px solid; float: right; font-size:12px; border-bottom: None;" width="49.9%" height="86px">
		        <tr>
		            <td style="font-size:small;">
		                <b>${"SPECIAL INSTRUCTION :"}</b>
		                <input type="checkbox" style= "text-align:right" name="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}" value="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}" id="${o.sale_id and o.sale_id.incoterm.name or 'UnDefined'}"
		                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
		                       checked
		                     %endif
		                />${'Master Bill of Lading'}
		            </td>
		        </tr>
		        <tr>
		            <td>
		                ${"Delivery before Noon"} <br/>
		            </td>
		        </tr>
		            <td style=" text-align:left; color:white;">
		                <br/>
		            </td>
		            <td style=" text-align:left; color:white;">
		                <br/>
		            </td>
		        </tr>
		        </table>
		        <table style="display: inline-block; border: 1px solid; float: left; border-bottom: None; border-left: 1px solid black; font-size:12px; " width="49.7%" height="60px">
		        <tr>
		            <td>
		                ${"Name :"}
		                    %if o.sale_id and o.sale_id.third_party_bill_to_id:
		                        ${o.sale_id.third_party_bill_to_id.name or '' | entity}
		                    %endif
		            </td>
		        </tr>
		        <tr>
		            <td>
		                ${"Address:"}
		                %if o.sale_id and o.sale_id.third_party_bill_to_id:
		                        %if o.sale_id.third_party_bill_to_id.street:
		                            ${o.sale_id.third_party_bill_to_id.street or ''},
		                        %endif
		                        %if o.sale_id.third_party_bill_to_id.street2:
		                            ${o.sale_id.third_party_bill_to_id.street2 or ''},
		                        %endif
		                        %if o.sale_id.third_party_bill_to_id.city:
		                            ${o.sale_id.third_party_bill_to_id.city or ''},
		                        %endif
		                        %if o.sale_id.third_party_bill_to_id.state_id:
		                            ${o.sale_id.third_party_bill_to_id.state_id.name or ''},
		                        %endif
		                        %if o.sale_id.third_party_bill_to_id.zip:
		                            ${o.sale_id.third_party_bill_to_id.zip or ''},
		                        %endif
		                        %if o.sale_id.third_party_bill_to_id.country_id:
		                            ${o.sale_id.third_party_bill_to_id.country_id.name  or ''}
		                        %endif
		                %endif
		            </td>
		        </tr>
		        </tr>
					<td style=" text-align:left; color:white;">
						<br/>
					</td>
				</tr>
		        </table>
		        <table class="table4"  width="100%">
		            <tr>
		                <td width="5%">
		                    ${'HU'}
		                </td>
		                <td width="8%">
		                    ${'HU Type'}
		                </td>
		                <td width="8%">
		                    ${'PKGs'}
		                </td>
		                <td width="8%">
		                    ${'PKG type'}
		                </td>
		                <td width="5%">
		                    ${'HM'}
		                </td>
		                <td width="38%">
		                    ${'Description of Articles, Special Marks & Exceptions'}
		                </td>
		                <td width="8%">
		                    ${'NMFC#'}
		                </td>
		                <td width="8%">
		                    ${'Class'}
		                </td>
		                <td width="12%">
		                    ${'Weight Subj. to Correction'}
		                </td>
		            </tr>
		        </table>
		        %endif
			%endif
			%if line_count % 5 != 0:
				<table class="table5"  width="100%" height="55.5">
					<tr>
						%if get_type(line):
							<td width="5%">
							    %if line.product_packaging and line.product_packaging.qty:
								 ${int(round(line.product_qty / line.product_packaging.qty))}
								%endif
							</td>
							<td width="8%">
							   %if line and line.product_packaging and line.product_packaging.hu_type_id:
								  ${line.product_packaging.hu_type_id.name or '' |entity}
							   %endif
							</td>
							<td width="8%">
								${line.product_qty or '' |entity}
							</td>
							<td width="8%">
								${line.product_uom.name or '' |entity}
							</td>
							<td width="5%">
							</td>
							<td width="38%">
								[${line.product_id.code or '' |entity}] [${line.product_id.cust_code or '' | entity}] ${line.product_id.name or '' |entity}
							</td>
							<td width="8%">
								${o.nmfc or '' | entity}
							</td>
							<td width="8%">
								${o.p_class or '' | entity}
							</td>
							<td width="12%">
							     ${int(round(net_weight(line))) or 0 | entity}
							     <%  total = total +int(round(net_weight(line)))%>
							</td>
						%endif
						%if not get_type(line):
							<td width="5%">
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="5%">
							</td>
							<td style="text-align:left; " width="38%">
								   ${line}
							</td>
							<td width="8%">
							</td>
							<td width="8%">
							</td>
							<td width="12%">
							</td>
						%endif
					</tr>
				</table>
			%endif
		%endfor
		%if line_count % 5 != 0:
		<table class="table5" width='100%' height="80">
		%for i in range(0,5 -(line_count%5)):
			<tr>
					<td width="5%">
					</td>
					<td width="8%">
					</td>
					<td width="8%">
					</td>
					<td width="8%">
					</td>
					<td width="5%">
					</td>
					<td width="38%">
					</td>
					<td width="8%">
					</td>
					<td width="8%">
					</td>
					<td width="12%">
					</td>
				</tr>
			%endfor
		</table>
		%endif
		<table class="table5"  width="100%">
			<tr>
				<td style="border-bottom:1px solid black;" width="5%">

				</td>
				<td style="border-bottom:1px solid black;" width="8%">

				</td>
				<td width="8%">

				</td>
				<td style="text-align:right; border-bottom:1px solid black;" width="67%" colspan="5">
					<b>${'Total for All Pages(Weight in lbs)'}</b>
				</td>
				<td style="border-bottom:1px solid black;" width="12%">
					${total or 0.0 | entity}
				</td>
			</tr>
			</table>
			<table class="table5"  width="100%" height="30px" style="font-size:10px; ">
				<tr>
					<td style="border-bottom:1px solid black; text-align:top" width="35%">
						${'Hazardous Material Emergency Contact:'}
					</td>
					<td style="text-align:left; border-bottom:1px solid black;" width="15%">
						<b><u>${'Freight Term :'}</u></b><br/>

					 <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'Prepaid':
                       checked
                     %endif
                     />${'Prepaid'} <br/>

                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'Receiver':
                       checked
                     %endif
                     />${'Collect'}<br/>

                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'Third Party'}<br/>

					</td>
					<td style=" text-align:left; border-bottom:1px solid black;" width="50%">
						<b><u>${'C.O.D  Amount:'}</u></b><br/>
						&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
						 <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
	                     %if o.sale_id and o.sale_id.incoterm.name == 'Prepaid':
	                       checked
	                     %endif
                     	/>${'Prepaid'} <br/>

                     	&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
                     	<input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     	%if o.sale_id and o.sale_id.incoterm.name == 'Receiver':
                       		checked
                     	%endif
                     />${'Collect'}<br/>

                     &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&nbsp;
                      <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'Customer Check Acceptable'}<br/>
					</td>
				</tr>
			</table>
			<table class="table7"  width="100%" >
				<tr>
					<td style=" text-align:left; font-size:9px; border:1px solid black;" width="50%" height="5px">
						${'DECLARED VALUE :Where the rate is dependent on value,shippers are required to state specifically in writing the agreed of declared value of the property as follows.'}<br/>
						${'The agreed of declared value of the property is specifically stated by the shipper to be not'} <br/><br/>

						${'exceeding____________________________ per ____________________________'} <br/><br/>

					</td>
					<td style=" text-align:left; font-size:9px; border:1px solid black;" width="50%" height="5px">
						${'The carrier shall not make delivery of the shipment without payment of freight and all other lawful \n charges'} <br/>
						${'______________________________________Shipper Signature'}

					</td>
				</tr>
			</table>
			<table class="table7"  width="100%">
				<tr>
					<td style=" text-align:left; border:1px solid black; font-size:10px;" width="50%">
						${'NOTE Liability Limitation for loss of damage in this shipment may be applicable. See 49 U.S.C - 14706(c)(1)(A) and (B) '}<br/>
					</td>
				</tr>
			</table>
			<table class="table7"  width="100%" >
				<tr>
					<td style=" text-align:left; border:1px solid black; font-size:10px;" width="50%">
						${'RECEIVED Subject to individually determined rates or contracts that have been agreed upon in writing between the carrier and shipper, if applicable otherwise to the rates'}
						${'classifications and rules that have been established by the carrier and are available to the shipper on request. The property described above, in apparent good order except as noted'}
						${'(contents and condition of packages unknown) marked, consigned and destined as show above, which said carrier agrees to carry to destination, if on its route or otherwise deliver to another carrier'}
						${'on the route to destination. Every service to be performed hereunder shall be subject to all bill of lading terms and conditions in the governing classification on the date of the'}
						${'shipment. Shipper here by certifier that is here by familiar with all the bill of lading terms and conditions in the governing classification and the said terms and conditions are here by '}
						${'agreed to by the shipper and accepted for himself and his assigns'}
					</td>
				</tr>
				<tr>
					<td style=" text-align:left; border:1px solid black; font-size:9px;" width="50%" height="18px">
						${'This is to certify that the above named materials and property classified,described, packaged,marked and labeled. and are in proper condition of transaction according to the applicable'}
						${'regulations of the Department of Transportation '}
					</td>
				</tr>
			</table>
			<table class="table7"  width="100%">
				<tr>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'SHIPPER COMPANY NAME'} <br/>
						${company.name}
					</td>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'CARRIER'} <br/>
					</td>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'CONSIGNEE'} <br/>
					</td>
					<td style=" text-align:left; border-bottom:0px solid white; font-size:8px;" width="25%">
						<u> ${'TRAILER LOADED'} </u><br/>

					<input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'By Shipper'}<br/>
                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'By Driver'}<br/>

					</td>
				</tr>
				<tr>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'SHIPPING SIGNATURE/DATE'} <br/>
					</td>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'DRIVER SIGNATURE/DATE'} <br/>
					</td>
					<td style=" text-align:left; border:1px solid black; font-size:8px;" width="25%">
						${'CONSIGNEE SIGNATURE/DATE'} <br/>
					</td>
					<td style=" text-align:left; border-bottom:1px solid black; font-size:8px;" width="25%">
						<u> ${'FREIGHT COUNTER'} </u><br/>

					<input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'By Shipper'}<br/>

                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'By Driver/Pallets said to contain'}<br/>

                     <input type="checkbox" name="${o.sale_id and o.sale_id.incoterm.name or ''}" value="${o.sale_id and o.sale_id.incoterm.name or ''}"id="${o.sale_id and o.sale_id.incoterm or False}"
                     %if o.sale_id and o.sale_id.incoterm.name == 'thirdparty':
                       checked
                     %endif
                     />${'By Driver/Pieces'}<br/>
					</td>
				</tr>
			</table>
			
			%endfor
</body>
</html>