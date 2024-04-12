<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="18008000">
	<Item Name="My Computer" Type="My Computer">
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="full" Type="Folder">
			<Item Name="TwoProtocolLoop.vi" Type="VI" URL="../full/TwoProtocolLoop.vi"/>
		</Item>
		<Item Name="high-level" Type="Folder">
			<Item Name="RunProtocolCompletely.vi" Type="VI" URL="../high-level/RunProtocolCompletely.vi"/>
			<Item Name="StartRunningCurrentProtocol.vi" Type="VI" URL="../high-level/StartRunningCurrentProtocol.vi"/>
			<Item Name="StartRunningNamedProtocol.vi" Type="VI" URL="../high-level/StartRunningNamedProtocol.vi"/>
			<Item Name="WaitUntilIdle.vi" Type="VI" URL="../high-level/WaitUntilIdle.vi"/>
			<Item Name="WaitUntilRunning.vi" Type="VI" URL="../high-level/WaitUntilRunning.vi"/>
			<Item Name="WaitUntilStatus.vi" Type="VI" URL="../high-level/WaitUntilStatus.vi"/>
		</Item>
		<Item Name="low-level" Type="Folder">
			<Item Name="GetCurrentProtocol.vi" Type="VI" URL="../low-level/GetCurrentProtocol.vi"/>
			<Item Name="GetProtocolProgress.vi" Type="VI" URL="../low-level/GetProtocolProgress.vi"/>
			<Item Name="GetProtocolState.vi" Type="VI" URL="../low-level/GetProtocolState.vi"/>
			<Item Name="SetCurrentProtocol.vi" Type="VI" URL="../low-level/SetCurrentProtocol.vi"/>
			<Item Name="SetProtocolState.vi" Type="VI" URL="../low-level/SetProtocolState.vi"/>
		</Item>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="vi.lib" Type="Folder">
				<Item Name="Check if File or Folder Exists.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/libraryn.llb/Check if File or Folder Exists.vi"/>
				<Item Name="Clear Errors.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Clear Errors.vi"/>
				<Item Name="Error Cluster From Error Code.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Error Cluster From Error Code.vi"/>
				<Item Name="LabVIEWHTTPClient.lvlib" Type="Library" URL="/&lt;vilib&gt;/httpClient/LabVIEWHTTPClient.lvlib"/>
				<Item Name="NI_FileType.lvlib" Type="Library" URL="/&lt;vilib&gt;/Utility/lvfile.llb/NI_FileType.lvlib"/>
				<Item Name="NI_PackedLibraryUtility.lvlib" Type="Library" URL="/&lt;vilib&gt;/Utility/LVLibp/NI_PackedLibraryUtility.lvlib"/>
				<Item Name="NI_WebServices.lvlib" Type="Library" URL="/&lt;vilib&gt;/wsapi/NI_WebServices.lvlib"/>
				<Item Name="Path To Command Line String.vi" Type="VI" URL="/&lt;vilib&gt;/AdvancedString/Path To Command Line String.vi"/>
				<Item Name="PathToUNIXPathString.vi" Type="VI" URL="/&lt;vilib&gt;/Platform/CFURL.llb/PathToUNIXPathString.vi"/>
				<Item Name="REST Client.lvlib" Type="Library" URL="/&lt;vilib&gt;/addons/_JKI.lib/REST Client/REST Client.lvlib"/>
				<Item Name="Space Constant.vi" Type="VI" URL="/&lt;vilib&gt;/dlg_ctls.llb/Space Constant.vi"/>
				<Item Name="Trim Whitespace.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Trim Whitespace.vi"/>
				<Item Name="whitespace.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/whitespace.ctl"/>
			</Item>
		</Item>
		<Item Name="Build Specifications" Type="Build"/>
	</Item>
</Project>
