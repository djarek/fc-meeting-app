 <script type="text/javascript">
            
            tinymce.init({
                selector: '.editor-base',
                height: 400,                
                menubar: false,
                toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
                skin_url: 'css/vendor/tinymce',
                content_css: 'css/vendor/tinymce/content-style.css'
            });
            
            tinymce.init({
                selector: '.editor-full',
                height: 400,                
                plugins: [
                  'advlist autolink lists link image charmap print preview hr anchor pagebreak',
                  'searchreplace wordcount visualblocks visualchars code fullscreen',
                  'insertdatetime media nonbreaking save table contextmenu directionality',
                  'emoticons template paste textcolor colorpicker textpattern imagetools'
                ],
                toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
                toolbar2: 'print preview media | forecolor backcolor emoticons',
                image_advtab: true,
                skin_url: 'css/vendor/tinymce',
                content_css: 'css/vendor/tinymce/content-style.css'
            });
            
            $(document).ready(function(){
                $('.editor-summernote').summernote({
                    height: 400,
                    toolbar: [
                        // [groupName, [list of button]]
                        ['style', ['bold', 'italic', 'underline', 'clear']],
                        ['font', ['strikethrough', 'superscript', 'subscript']],
                        ['fontsize', ['fontsize']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph']],                        
                        ['insert', ['picture','link','video']]
                    ]
                });
                
                $(window).resize();
            });            
        </script>