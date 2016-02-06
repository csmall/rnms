<%inherit file="local:templates.master"/>
${about_tile.display() | n}

    <div class="row">
      <div class="col-md-12">
        <div class="page-header">
          <h2>About RoseNMS</h2>
        </div>
        <p>
          RoseNMS is a piece of Free Software that
          can monitor your network devices and servers. While based upon
          JFFNMS it has been completely re-written in python.
          The software would
not be possible without some contributing projects, including:
        </p>
        <ul>
          <li>TurboGears2 - A webframework</li>
          <li>JFFNMS - The predessor to this project written in PHP.</li>
          <li>RRDTool - Graphing and round robin database</li>
        </ul>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6">
       <h3>Copyright</h3>
       <p>
         RoseNMS is Copyright &copy; 2011,2012,2013,2014 Craig Small. This program is based upon the JFFNMS project
	 which was largely the work of Javier Szyszlican.
       </p>
      </div>
      <div class="col-md-6">
       <h3>About RoseNMS</h3>
       <p>
         Originally RoseNMS was called Rosenberg NMS and was named after
         Rosenberg's Heath Monitor is a large lizard found in Australia.
	 The name was shorted in 2015 to just RoseNMS which is a lot easier
	 to say and type.
       </p>
     </div>
   </div>
   <div class="row">
     <div class="span6">
       <div class="well" style="padding: 8px 0;">
         <h3>License</h3>
           <p>
	     This program is free software; you can redistribute it and/or modify
             it under the terms of the GNU General Public License as published by
             the Free Software Foundation; either version 2 of the License, or
             (at your option) any later version.
           </p><p>
             This program is distributed in the hope that it will be useful,
             but WITHOUT ANY WARRANTY; without even the implied warranty of
             MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
             GNU General Public License for more details.
           </p><p>
             You should have received a copy of the GNU General Public License along
             with this program; if not, write to the Free Software Foundation, Inc.,
             51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
           </p>
         </div>
       </div>
    </div>
