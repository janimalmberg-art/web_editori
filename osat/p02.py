BASE_TEMPLATE += """/* ---- Tekstikehys ---- */
.text-frame {
    border: 1px solid #aaa;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    background: #fff;
    line-height: 1.6;
}
.text-frame .frame-title {
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 8px;
    border-bottom: 1px solid #eee;
    padding-bottom: 4px;
}
/* ---- Objektikehys (kaavio / upotettu objekti) ---- */
.object-frame {
    border: 2px dashed #666;
    padding: 15px;
    margin: 10px 0;
    border-radius: 4px;
    background: #fafafa;
}
.object-frame .frame-title {
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 8px;
}
/* ---- Kalenteri ---- */
.calendar {
    border: 1px solid #ccc;
    padding: 15px;
    display: inline-block;
    border-radius: 4px;
    background: #fff;
}
.calendar h3 {
    margin-top: 0;
    text-align: center;
}
.calendar table {
    border-collapse: collapse;
}
.calendar th {
    background-color: #0078d7;
    color: white;
    padding: 8px 12px;
    text-align: center;
}
.calendar td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: center;
    width: 50px;
    height: 40px;
}
.calendar td.empty {
    background-color: #f0f0f0;
}
/* ---- Alasivu / osio ---- */
.subpage {
    border-left: 4px solid #0078d7;
    padding: 10px 15px;
    margin: 20px 0;
    background: #fff;
    border-radius: 0 4px 4px 0;
}
/* ---- Taulukko ---- */
.data-table {
    border-collapse: collapse;
    margin: 10px 0;
}
.data-table th,
.data-table td {
    border: 1px solid #999;
    padding: 8px 12px;
}
.data-table th {
    background-color: #0078d7;
    color: #fff;
}
.data-table tr:nth-child(even) td {
    background-color: #f2f7fc;
}
/* ---- Video ---- */
.video-embed {
    margin: 10px 0;
}
.video-embed iframe {
    max-width: 100%;
    border: 0;
    border-radius: 4px;
}
/* ---- Lainaus ---- */
blockquote {
    border-left: 4px solid #0078d7;
    padding: 8px 16px;
    margin: 10px 0;
    background: #eef5fc;
    color: #444;
    font-style: italic;
    border-radius: 0 4px 4px 0;
}
/* ---- Yleiset ---- */
h1, h2, h3 {
    color: #222;
}
.content a {
    color: #0066cc;
}
.center {
    text-align: center;
}
.content {
    max-width: 900px;
    margin: 0 auto;
}
</style>
</head>
<body>

<div class="navbar">
  <a href="#">Etusivu</a>
</div>

<div class="content">
  <h1>Sivun otsikko</h1>
  <p>Klikkaa tätä tekstiä ja kirjoita suoraan – muokkaus onnistuu ilman koodaamista.</p>
@CONTENT@
</div>

</body>
</html>
"""